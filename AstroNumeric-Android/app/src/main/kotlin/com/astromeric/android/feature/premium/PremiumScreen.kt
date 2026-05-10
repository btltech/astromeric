package com.astromeric.android.feature.premium

import android.app.Activity
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Badge
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.android.billingclient.api.ProductDetails
import com.astromeric.android.R
import com.astromeric.android.core.data.billing.SubscriptionRepository
import com.astromeric.android.core.data.billing.SubscriptionSku

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PremiumScreen(
    subscriptionRepository: SubscriptionRepository,
    isPremiumUser: Boolean,
    onBack: () -> Unit,
) {
    val context = LocalContext.current
    val activity = context as? Activity
    val productDetails by subscriptionRepository.productDetails.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(stringResource(R.string.premium_screen_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.action_back),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            // Hero
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(
                    imageVector = Icons.Filled.AutoAwesome,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp),
                    tint = MaterialTheme.colorScheme.primary,
                )
                Text(
                    text = if (isPremiumUser) {
                        stringResource(R.string.premium_hero_title_active)
                    } else {
                        stringResource(R.string.premium_hero_title)
                    },
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center,
                )
                Text(
                    text = if (isPremiumUser) {
                        stringResource(R.string.premium_hero_body_active)
                    } else {
                        stringResource(R.string.premium_hero_body)
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )
            }

            Spacer(Modifier.height(4.dp))

            // Feature list
            PremiumFeatureList()

            Spacer(Modifier.height(4.dp))

            if (!isPremiumUser) {
                // Plan cards
                val monthlyProduct = productDetails.firstOrNull { it.productId == SubscriptionSku.MONTHLY.productId }
                val yearlyProduct = productDetails.firstOrNull { it.productId == SubscriptionSku.YEARLY.productId }
                val lifetimeProduct = productDetails.firstOrNull { it.productId == SubscriptionSku.LIFETIME.productId }

                Text(
                    text = stringResource(R.string.premium_plans_title),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )

                yearlyProduct?.let { product ->
                    PremiumPlanCard(
                        title = stringResource(R.string.premium_plan_yearly_title),
                        price = product.subscriptionOfferDetails
                            ?.firstOrNull()
                            ?.pricingPhases
                            ?.pricingPhaseList
                            ?.firstOrNull()
                            ?.formattedPrice
                            ?: stringResource(R.string.premium_plan_yearly_fallback_price),
                        description = stringResource(R.string.premium_plan_yearly_description),
                        badge = stringResource(R.string.premium_plan_yearly_badge),
                        isHighlighted = true,
                        onSubscribe = {
                            activity?.let { act ->
                                val offerToken = product.subscriptionOfferDetails
                                    ?.firstOrNull()
                                    ?.offerToken
                                subscriptionRepository.launchPurchaseFlow(act, product, offerToken)
                            }
                        },
                    )
                }

                monthlyProduct?.let { product ->
                    PremiumPlanCard(
                        title = stringResource(R.string.premium_plan_monthly_title),
                        price = product.subscriptionOfferDetails
                            ?.firstOrNull()
                            ?.pricingPhases
                            ?.pricingPhaseList
                            ?.firstOrNull()
                            ?.formattedPrice
                            ?: stringResource(R.string.premium_plan_monthly_fallback_price),
                        description = stringResource(R.string.premium_plan_monthly_description),
                        badge = null,
                        isHighlighted = false,
                        onSubscribe = {
                            activity?.let { act ->
                                val offerToken = product.subscriptionOfferDetails
                                    ?.firstOrNull()
                                    ?.offerToken
                                subscriptionRepository.launchPurchaseFlow(act, product, offerToken)
                            }
                        },
                    )
                }

                lifetimeProduct?.let { product ->
                    PremiumPlanCard(
                        title = stringResource(R.string.premium_plan_lifetime_title),
                        price = product.oneTimePurchaseOfferDetails?.formattedPrice
                            ?: stringResource(R.string.premium_plan_lifetime_fallback_price),
                        description = stringResource(R.string.premium_plan_lifetime_description),
                        badge = null,
                        isHighlighted = false,
                        onSubscribe = {
                            activity?.let { act ->
                                subscriptionRepository.launchPurchaseFlow(act, product, null)
                            }
                        },
                    )
                }

                if (productDetails.isEmpty()) {
                    PremiumPlaceholderCards(onBack = onBack)
                }

                Spacer(Modifier.height(8.dp))
                Text(
                    text = stringResource(R.string.premium_legal_note),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
            } else {
                PremiumActiveCard()
            }
        }
    }
}

@Composable
private fun PremiumFeatureList() {
    val features = listOf(
        stringResource(R.string.premium_feature_ai_explanations),
        stringResource(R.string.premium_feature_unlimited_readings),
        stringResource(R.string.premium_feature_cloud_sync),
        stringResource(R.string.premium_feature_advanced_charts),
        stringResource(R.string.premium_feature_compatibility),
        stringResource(R.string.premium_feature_timing),
    )
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = stringResource(R.string.premium_whats_included),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
            )
            features.forEach { feature ->
                Row(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = Icons.Filled.CheckCircle,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(18.dp),
                    )
                    Text(
                        text = feature,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
    }
}

@Composable
private fun PremiumPlanCard(
    title: String,
    price: String,
    description: String,
    badge: String?,
    isHighlighted: Boolean,
    onSubscribe: () -> Unit,
) {
    val borderColor = if (isHighlighted) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.outlineVariant
    }
    val containerColor = if (isHighlighted) {
        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
    } else {
        MaterialTheme.colorScheme.surface
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(
                width = if (isHighlighted) 2.dp else 1.dp,
                color = borderColor,
                shape = RoundedCornerShape(12.dp),
            ),
        colors = CardDefaults.cardColors(containerColor = containerColor),
        shape = RoundedCornerShape(12.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                badge?.let {
                    Badge(
                        containerColor = MaterialTheme.colorScheme.primary,
                    ) {
                        Text(
                            text = it,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        )
                    }
                }
            }
            Text(
                text = price,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.height(4.dp))
            if (isHighlighted) {
                Button(
                    onClick = onSubscribe,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.premium_cta_subscribe))
                }
            } else {
                OutlinedButton(
                    onClick = onSubscribe,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.premium_cta_subscribe))
                }
            }
        }
    }
}

@Composable
private fun PremiumPlaceholderCards(onBack: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.premium_unavailable_title),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = stringResource(R.string.premium_unavailable_body),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            OutlinedButton(onClick = onBack) {
                Text(stringResource(R.string.action_back))
            }
        }
    }
}

@Composable
private fun PremiumActiveCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.4f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Icon(
                imageVector = Icons.Filled.CheckCircle,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(32.dp),
            )
            Text(
                text = stringResource(R.string.premium_active_title),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center,
            )
            Text(
                text = stringResource(R.string.premium_active_body),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }
    }
}
