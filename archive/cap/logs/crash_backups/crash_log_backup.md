## Crash Details

**Crash Thread**: `Thread[main,5,main]`  
**Crash Timestamp**: `2026-04-06 14:55:57.242 UTC`  

**Crash Message**:
```
setSpan (-1 ... -1) starts before 0
```


### Stacktrace

```
java.lang.IndexOutOfBoundsException: setSpan (-1 ... -1) starts before 0
	at android.text.SpannableStringBuilder.checkRange(SpannableStringBuilder.java:1332)
	at android.text.SpannableStringBuilder.setSpan(SpannableStringBuilder.java:686)
	at android.text.SpannableStringBuilder.setSpan(SpannableStringBuilder.java:678)
	at android.text.Selection.setSelection(Selection.java:96)
	at android.text.Selection.setSelection(Selection.java:80)
	at android.text.method.ArrowKeyMovementMethod.onTouchEvent(ArrowKeyMovementMethod.java:333)
	at android.widget.TextView.onTouchEvent(TextView.java:13335)
	at android.view.View.performOnTouchCallback(View.java:16741)
	at android.view.View.dispatchTouchEvent(View.java:16694)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3149)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:2830)
	at com.android.internal.policy.DecorView.superDispatchTouchEvent(DecorView.java:496)
	at com.android.internal.policy.PhoneWindow.superDispatchTouchEvent(PhoneWindow.java:2040)
	at android.app.Activity.dispatchTouchEvent(Activity.java:4733)
	at com.android.internal.policy.DecorView.dispatchTouchEvent(DecorView.java:454)
	at android.view.View.dispatchPointerEvent(View.java:17043)
	at android.view.ViewRootImpl$ViewPostImeInputStage.processPointerEvent(ViewRootImpl.java:8724)
	at android.view.ViewRootImpl$ViewPostImeInputStage.onProcess(ViewRootImpl.java:8471)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:7851)
	at android.view.ViewRootImpl$InputStage.onDeliverToNext(ViewRootImpl.java:7908)
	at android.view.ViewRootImpl$InputStage.forward(ViewRootImpl.java:7874)
	at android.view.ViewRootImpl$AsyncInputStage.forward(ViewRootImpl.java:8040)
	at android.view.ViewRootImpl$InputStage.apply(ViewRootImpl.java:7882)
	at android.view.ViewRootImpl$AsyncInputStage.apply(ViewRootImpl.java:8097)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:7855)
	at android.view.ViewRootImpl$InputStage.onDeliverToNext(ViewRootImpl.java:7908)
	at android.view.ViewRootImpl$InputStage.forward(ViewRootImpl.java:7874)
	at android.view.ViewRootImpl$InputStage.apply(ViewRootImpl.java:7882)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:7855)
	at android.view.ViewRootImpl.deliverInputEvent(ViewRootImpl.java:11224)
	at android.view.ViewRootImpl.doProcessInputEvents(ViewRootImpl.java:11140)
	at android.view.ViewRootImpl.enqueueInputEvent(ViewRootImpl.java:11099)
	at android.view.ViewRootImpl$WindowInputEventReceiver.onInputEvent(ViewRootImpl.java:11371)
	at android.view.InputEventReceiver.dispatchInputEvent(InputEventReceiver.java:307)
	at android.view.InputEventReceiver.nativeConsumeBatchedInputEvents(Native Method)
	at android.view.InputEventReceiver.consumeBatchedInputEvents(InputEventReceiver.java:266)
	at android.view.ViewRootImpl.doConsumeBatchedInput(ViewRootImpl.java:11323)
	at android.view.ViewRootImpl$ConsumeBatchedInputRunnable.run(ViewRootImpl.java:11464)
	at android.view.Choreographer$CallbackRecord.run(Choreographer.java:1695)
	at android.view.Choreographer$CallbackRecord.run(Choreographer.java:1704)
	at android.view.Choreographer.doCallbacks(Choreographer.java:1288)
	at android.view.Choreographer.doFrame(Choreographer.java:1167)
	at android.view.Choreographer$FrameDisplayEventReceiver.run(Choreographer.java:1678)
	at android.os.Handler.handleCallback(Handler.java:1037)
	at android.os.Handler.dispatchMessage(Handler.java:108)
	at android.os.Looper.loopOnce(Looper.java:304)
	at android.os.Looper.loop(Looper.java:430)
	at android.app.ActivityThread.main(ActivityThread.java:9345)
	at java.lang.reflect.Method.invoke(Native Method)
	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:593)
	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:953)

```
##


## Termux App Info

**APP_NAME**: `Termux`  
**PACKAGE_NAME**: `com.termux`  
**VERSION_NAME**: `0.118.3`  
**VERSION_CODE**: `1002`  
**TARGET_SDK**: `28`  
**IS_DEBUGGABLE_BUILD**: `false`  
**SE_PROCESS_CONTEXT**: `u:r:untrusted_app_27:s0:c103,c257,c512,c768`  
**SE_FILE_CONTEXT**: `u:object_r:app_data_file:s0:c103,c257,c512,c768`  
**SE_INFO**: `default:targetSdkVersion=28:complete`  
**APK_RELEASE**: `F-Droid`  
**SIGNING_CERTIFICATE_SHA256_DIGEST**: `228FB2CFE90831C1499EC3CCAF61E96E8E1CE70766B9474672CE427334D41C42`  
##


## Device Info

### Software

**OS_VERSION**: `6.1.141-android14-11-g2403eaeca101-ab14281579`  
**SDK_INT**: `36`  
**RELEASE**: `16`  
**ID**: `W1UI36H.39-17`  
**DISPLAY**: `W1UI36H.39-17`  
**INCREMENTAL**: `0fec32-411f86`  
**SECURITY_PATCH**: `2026-02-01`  
**IS_TREBLE_ENABLED**: `true`  
**TYPE**: `user`  
**TAGS**: `release-keys`  

### Hardware

**MANUFACTURER**: `motorola`  
**BRAND**: `motorola`  
**MODEL**: `motorola edge 50 neo`  
**PRODUCT**: `vienna_g_syss`  
**BOARD**: `vienna`  
**HARDWARE**: `mt6878`  
**DEVICE**: `vienna`  
**SUPPORTED_ABIS**: `arm64-v8a`  
**SUPPORTED_32_BIT_ABIS**:   
**SUPPORTED_64_BIT_ABIS**: `arm64-v8a`  
**PAGE_SIZE**: `4096`  
##
