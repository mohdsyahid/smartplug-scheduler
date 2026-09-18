# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# Keep network calls
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn okhttp3.**
-dontwarn okio.**

# Keep JSON classes
-keep class org.json.** { *; }
-keep class * extends org.json.JSONObject

# Keep data models
-keepclassmembers class ** {
    @org.json.JsonProperty <methods>;
}

# OkHttp & Retrofit
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase
-dontnote okhttp3.**
-dontwarn okhttp3.**
-dontwarnokhttp3.Internal

# Kotlin coroutines
-keep class kotlinx.coroutines.** { *; }
-dontwarn kotlinx.coroutines.**

# General Android
-keep class android.support.v7.** { *; }
-dontwarn android.support.**

# Preserve custom view attributes
-keep class * extends android.view.View {
    @android.support.annotation.AttrRes <fields>;
}
