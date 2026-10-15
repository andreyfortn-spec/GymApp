package com.example.gym

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.webkit.WebView
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.net.InetSocketAddress
import java.net.Socket

class MainActivity : Activity() {
    private lateinit var web: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.parseColor("#1B1F27")
        web = WebView(this)
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.setBackgroundColor(Color.parseColor("#ECEDEF"))
        setContentView(web)
        web.loadData("<body style='font-family:sans-serif;padding:32px'>Запуск сервера…</body>", "text/html", "utf-8")

        if (!Python.isStarted()) Python.start(AndroidPlatform(this))

        if (!serverStarted) {
            serverStarted = true
            val db = filesDir.absolutePath + "/gym.db"
            Thread {
                Python.getInstance().getModule("server").callAttr("run", db, PORT)
            }.start()
        }

        Thread {
            repeat(120) {
                try {
                    Socket().use { it.connect(InetSocketAddress("127.0.0.1", PORT), 200) }
                    runOnUiThread { web.loadUrl("http://127.0.0.1:$PORT/") }
                    return@Thread
                } catch (e: Exception) { Thread.sleep(250) }
            }
            runOnUiThread { web.loadData("Сервер не запустился", "text/plain", "utf-8") }
        }.start()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() { moveTaskToBack(true) }

    companion object {
        const val PORT = 8765
        @Volatile var serverStarted = false
    }
}
