# AstroNumeric Android — R8/ProGuard keep rules.
#
# NOTE: release `isMinifyEnabled` is currently false. These rules are staged so
# minification can be safely turned on after a verified release build. They keep
# the data classes that Gson (de)serializes by reflection and the Retrofit API.

# --- App data/model classes (Gson reflection by field name) ---
-keep class com.astromeric.android.core.model.** { *; }
-keepclassmembers class com.astromeric.android.core.model.** { <fields>; }

# --- Gson ---
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken
-keepclassmembers,allowobfuscation class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# --- Retrofit / OkHttp ---
-keepattributes RuntimeVisibleAnnotations,RuntimeVisibleParameterAnnotations
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response
-dontwarn okhttp3.**
-dontwarn okio.**
-dontwarn javax.annotation.**

# --- Kotlin coroutines ---
-dontwarn kotlinx.coroutines.**

# --- Keep Retrofit service interfaces in this app ---
-keep interface com.astromeric.android.core.data.remote.** { *; }
