package parth.assistant.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.graphics.Rect
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * Phone-use engine (unprivileged mode): reads the screen layout tree and
 * performs taps/swipes/text entry like a human user. Paired with
 * [parth.assistant.shizuku.ShizukuBridge] for privileged system operations.
 *
 * Design notes (docs/04 §1):
 *  - vision-model grounding (screenshot → VLM → coordinates) is layered on top
 *    of the layout tree so modded apps with obfuscated views still work;
 *  - event-driven (no polling) to stay battery-friendly;
 *  - waits for window transitions with a timeout instead of fixed sleeps.
 */
class PhoneControlAccessibilityService : AccessibilityService() {

    companion object {
        @Volatile
        var instance: PhoneControlAccessibilityService? = null
            private set
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Feed screen-state events to the executor's wait-for-state steps.
    }

    override fun onInterrupt() {}

    override fun onDestroy() {
        instance = null
        super.onDestroy()
    }

    // ------------------------------------------------------------- read screen
    /** Serializable snapshot of the current screen for the vision/planner layer. */
    fun dumpScreen(): List<Node> {
        val root = rootInActiveWindow ?: return emptyList()
        val out = mutableListOf<Node>()
        walk(root, out, depth = 0)
        return out
    }

    private fun walk(node: AccessibilityNodeInfo, out: MutableList<Node>, depth: Int) {
        out.add(Node(depth, node.viewIdResourceName, node.text?.toString(),
            node.contentDescription?.toString(), Rect().also { node.getBoundsInScreen(it) }))
        for (i in 0 until node.childCount) node.getChild(i)?.let { walk(it, out, depth + 1) }
    }

    data class Node(val depth: Int, val viewId: String?, val text: String?,
                    val description: String?, val bounds: Rect)

    // ------------------------------------------------------------- act
    fun tap(x: Float, y: Float): Boolean = dispatchGesture(
        GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(Path().apply { moveTo(x, y) }, 0, 60))
            .build(), null, null)

    fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, durationMs: Long = 220): Boolean =
        dispatchGesture(
            GestureDescription.Builder()
                .addStroke(GestureDescription.StrokeDescription(
                    Path().apply { moveTo(x1, y1); lineTo(x2, y2) }, 0, durationMs))
                .build(), null, null)

    fun findNodeByText(text: String): AccessibilityNodeInfo? {
        val root = rootInActiveWindow ?: return null
        val nodes = root.findAccessibilityNodeInfosByText(text)
        return nodes?.firstOrNull()
    }

    fun clickNode(node: AccessibilityNodeInfo): Boolean {
        var target: AccessibilityNodeInfo? = node
        while (target != null && !target.isClickable) target = target.parent
        return target?.performAction(AccessibilityNodeInfo.ACTION_CLICK) ?: false
    }

    fun typeText(node: AccessibilityNodeInfo, text: String): Boolean {
        val args = android.os.Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        }
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
    }

    fun goBack(): Boolean = performGlobalAction(GLOBAL_ACTION_BACK)
    fun goHome(): Boolean = performGlobalAction(GLOBAL_ACTION_HOME)
    fun openNotifications(): Boolean = performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
}
