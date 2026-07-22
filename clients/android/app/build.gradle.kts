import java.io.ByteArrayOutputStream

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

fun gitCommitSha(): String {
    return try {
        val repoRoot = rootProject.projectDir.resolve("../..").canonicalFile
        val proc = ProcessBuilder("git", "rev-parse", "HEAD")
            .directory(repoRoot)
            .redirectErrorStream(true)
            .start()
        val out = ByteArrayOutputStream()
        proc.inputStream.copyTo(out)
        val code = proc.waitFor()
        val sha = out.toString(Charsets.UTF_8).trim()
        if (code == 0 && sha.matches(Regex("[0-9a-f]{40}"))) sha else "0000000000000000000000000000000000000000"
    } catch (_: Exception) {
        "0000000000000000000000000000000000000000"
    }
}

android {
    namespace = "org.gunnchos.edgeio"
    compileSdk = 34

    defaultConfig {
        applicationId = "org.gunnchos.edgeio"
        minSdk = 26
        targetSdk = 34
        versionCode = 5
        versionName = "0.3.2-gate3-android"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        buildConfigField("String", "GIT_COMMIT", "\"${gitCommitSha()}\"")
        buildConfigField("String", "FILE_PROVIDER_AUTHORITY_SUFFIX", "\".provider\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
        debug {
            applicationIdSuffix = ".debug"
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.activity:activity-ktx:1.8.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    testImplementation("junit:junit:4.13.2")
    // JVM unit tests need a real org.json implementation (Android stubs are not mocked).
    testImplementation("org.json:json:20240303")
}
