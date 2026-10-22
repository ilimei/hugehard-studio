# How to turn an iPhone video into a Live Photo

> On iPhone, open Workbench (“工作台”) in This Pic Can Change (Chinese app name: “这图能改”), choose Photo or Video (“选择照片或视频”), and import a video. In the editor’s bottom mode bar, select Live Photo (“实况”), select up to three seconds, set a cover, quality, and sound, then save the paired result to Photos. Conversion runs on device. The app supports iOS 17 and later and its interface is Simplified Chinese. The public TestFlight build 1.2 (5) is available to install; it is not on the App Store. iPad can run the iPhone compatibility layout.

[Join the public TestFlight beta · 1.2 (5)](https://testflight.apple.com/join/GK8ht2vv)

## Steps

1. In Workbench (“工作台”), choose Photo or Video (“选择照片或视频”) and import a video. In the editor’s bottom mode bar, select Live Photo (“实况”).
2. Select a segment on the timeline, up to three seconds. Preview plays the source segment; encoding begins after you choose Generate.
3. Choose a cover frame from inside the selected segment. Preview and export use the same frame.
4. Choose Original (“原尺寸”), HD (“高清”), or Compact (“小体积”) quality, then decide whether to keep source audio. The three settings cap the output long edge at 4,096, 1,920, and 1,280 pixels respectively; smaller footage is not enlarged. Source video with a long edge above 4,096 pixels is unsupported.
5. Generate and preview the paired photo and video assets, then save them to Photos. Conversion runs on device and does not upload the source video to the app developer’s servers.

## Compatibility and display limits

- Import and conversion depend on whether iOS can read the file and its encoding. MP4 is a container format; it does not guarantee that every video encoding inside it is supported. The app does not claim to support every video format.
- Highlights and colors in some HDR footage may look different from the source. The current version does not guarantee preservation of HDR appearance.
- Saving a Live Photo and setting a lock-screen live wallpaper are separate actions. The app creates and saves Live Photos but does not set wallpapers. Compatibility as a lock-screen wallpaper on specific devices and OS versions has not been verified and is not guaranteed.

## Video demonstration

[Watch the historical feature-demo recording](https://hugehard.app/assets/video-to-live-photo-demo.mp4). It was captured in the project’s simulator promotion workflow with waiting portions edited out. The 19-second clip length is not a conversion-time measurement. The app interface is Simplified Chinese; this recording may differ from version 1.2 (5).

## Related pages

- [Product overview](https://hugehard.app/en/apps/this-pic-can-change/)
- [Product support](https://hugehard.app/en/apps/this-pic-can-change/support.html)
- [HTML guide](https://hugehard.app/en/guides/video-to-live-photo/)
