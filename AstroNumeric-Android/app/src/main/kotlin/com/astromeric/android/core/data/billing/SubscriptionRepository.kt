package com.astromeric.android.core.data.billing

import android.app.Activity
import android.content.Context
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

enum class SubscriptionSku(val productId: String) {
    MONTHLY("com.astromeric.premium.monthly"),
    YEARLY("com.astromeric.premium.yearly"),
    LIFETIME("com.astromeric.premium.lifetime"),
}

class SubscriptionRepository(
    context: Context,
    private val preferencesStore: AppPreferencesStore,
) {
    private val repositoryScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private val _productDetails = MutableStateFlow<List<ProductDetails>>(emptyList())
    val productDetails: StateFlow<List<ProductDetails>> = _productDetails.asStateFlow()

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val purchasesUpdatedListener = PurchasesUpdatedListener { billingResult, purchases ->
        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            for (purchase in purchases) {
                handlePurchase(purchase)
            }
        }
    }

    private val billingClient: BillingClient = BillingClient.newBuilder(context.applicationContext)
        .setListener(purchasesUpdatedListener)
        .enablePendingPurchases()
        .build()

    init {
        connect()
    }

    private fun connect() {
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    _isConnected.value = true
                    repositoryScope.launch {
                        queryProductDetails()
                        restorePurchases()
                    }
                }
            }

            override fun onBillingServiceDisconnected() {
                _isConnected.value = false
            }
        })
    }

    fun queryProductDetails() {
        // Billing v6+ requires all products in a single query to share the same type.
        // Split into two calls: one for subscriptions, one for in-app (lifetime).
        val subsProducts = SubscriptionSku.entries
            .filter { it != SubscriptionSku.LIFETIME }
            .map { sku ->
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(sku.productId)
                    .setProductType(BillingClient.ProductType.SUBS)
                    .build()
            }
        val inappProducts = listOf(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(SubscriptionSku.LIFETIME.productId)
                .setProductType(BillingClient.ProductType.INAPP)
                .build(),
        )

        val combined = mutableListOf<ProductDetails>()

        val subsParams = QueryProductDetailsParams.newBuilder()
            .setProductList(subsProducts)
            .build()
        billingClient.queryProductDetailsAsync(subsParams) { subsResult, subsList ->
            if (subsResult.responseCode == BillingClient.BillingResponseCode.OK) {
                combined.addAll(subsList)
            }
            // Query in-app after subs regardless, then publish once both complete
            val inappParams = QueryProductDetailsParams.newBuilder()
                .setProductList(inappProducts)
                .build()
            billingClient.queryProductDetailsAsync(inappParams) { inappResult, inappList ->
                if (inappResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    combined.addAll(inappList)
                }
                _productDetails.value = combined.toList()
            }
        }
    }

    fun launchPurchaseFlow(
        activity: Activity,
        productDetails: ProductDetails,
        offerToken: String?,
    ) {
        val productDetailsParams = if (offerToken != null) {
            BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(productDetails)
                .setOfferToken(offerToken)
                .build()
        } else {
            BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(productDetails)
                .build()
        }

        val billingFlowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(productDetailsParams))
            .build()

        billingClient.launchBillingFlow(activity, billingFlowParams)
    }

    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            repositoryScope.launch {
                preferencesStore.setGooglePlayPremium(true)
                if (!purchase.isAcknowledged) {
                    val acknowledgePurchaseParams = AcknowledgePurchaseParams.newBuilder()
                        .setPurchaseToken(purchase.purchaseToken)
                        .build()
                    billingClient.acknowledgePurchase(acknowledgePurchaseParams) { _ -> }
                }
            }
        }
    }

    private fun restorePurchases() {
        // Restore subscriptions
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build(),
        ) { billingResult, purchaseList ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                val hasActiveSub = purchaseList.any { it.purchaseState == Purchase.PurchaseState.PURCHASED }
                if (!hasActiveSub) {
                    // Check in-app (lifetime) purchases before clearing
                    restoreInAppPurchases()
                } else {
                    for (purchase in purchaseList) handlePurchase(purchase)
                }
            }
        }
    }

    private fun restoreInAppPurchases() {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP)
                .build(),
        ) { billingResult, purchaseList ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                val hasLifetime = purchaseList.any {
                    it.purchaseState == Purchase.PurchaseState.PURCHASED &&
                        it.products.contains(SubscriptionSku.LIFETIME.productId)
                }
                repositoryScope.launch {
                    if (!hasLifetime) {
                        preferencesStore.setGooglePlayPremium(false)
                    } else {
                        for (purchase in purchaseList) handlePurchase(purchase)
                    }
                }
            }
        }
    }
}
