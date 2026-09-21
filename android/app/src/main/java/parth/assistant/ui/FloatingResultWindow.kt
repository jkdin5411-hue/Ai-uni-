package parth.assistant.ui

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.PixelFormat
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.LinearLayout
import android.widget.TextView

/**
 * PC/laptop-style floating result window on Android (SYSTEM_ALERT_WINDOW).
 *
 * Owner rule: after finishing work, Parth shows the result — by opening its
 * app AND/OR as a floating overlay with the summary, photos/videos and details.
 */
class FloatingResultWindow(private val context: Context) {

    private val wm = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    private var view: View? = null

    @SuppressLint("ClickableViewAccessibility")
    fun show(title: String, body: String) {
        dismiss()

        val layout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 24, 28, 24)
            setBackgroundColor(0xF2171A21.toInt())
        }
        val titleView = TextView(context).apply {
            text = title; textSize = 16f; setTextColor(0xFF7CDBFF.toInt())
        }
        val bodyView = TextView(context).apply {
            text = body; textSize = 13f; setTextColor(0xFFEDEDF4.toInt())
            setPadding(0, 12, 0, 0)
        }
        layout.addView(titleView)
        layout.addView(bodyView)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT,
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 48; y = 180
        }

        // drag to move
        var downX = 0f; var downY = 0f; var startX = 0; var startY = 0
        layout.setOnTouchListener { _, e ->
            when (e.action) {
                MotionEvent.ACTION_DOWN -> {
                    downX = e.rawX; downY = e.rawY; startX = params.x; startY = params.y; true
                }
                MotionEvent.ACTION_MOVE -> {
                    params.x = startX + (e.rawX - downX).toInt()
                    params.y = startY + (e.rawY - downY).toInt()
                    wm.updateViewLayout(layout, params); true
                }
                else -> false
            }
        }

        wm.addView(layout, params)
        view = layout
    }

    fun dismiss() {
        view?.let { wm.removeView(it) }
        view = null
    }
}
