# How to turn an iPhone video into a Live Photo

> Use This Pic Can Change (Chinese app name: “这图能改”) on iPhone or iPad to choose a video iOS can read, select up to three seconds, set a cover, quality, and sound, then save the paired result to Photos. Conversion runs on device. The app supports iOS 17 and later and its interface is Simplified Chinese. TestFlight 1.0 (2) external beta review is pending; screenshot delivery is in development and not included in this beta.

[View TestFlight (review pending)](https://testflight.apple.com/join/GK8ht2vv). The public page is not accepting testers yet; joining opens after Apple Beta Review approval.

## Steps

1. In Tools (“工具”), open Video to Live Photo (“视频转实况”) and import a video available to the iOS video picker.
2. Select a segment on the timeline, up to three seconds. Preview plays the source segment; encoding begins after you choose Generate.
3. Choose a cover frame from inside the selected segment. Preview and export use the same frame.
4. Choose Original (“原尺寸”), HD (“高清”), or Compact (“小体积”) quality, then decide whether to keep source audio. The three settings cap the output long edge at 4,096, 1,920, and 1,280 pixels respectively; smaller footage is not enlarged. Source video with a long edge above 4,096 pixels is unsupported.
5. Generate and preview the paired photo and video assets, then save them to Photos. Conversion runs on device and does not upload the source video to the app developer’s servers.

## Compatibility and display limits

- Import and conversion depend on whether iOS can read the file and its encoding. MP4 is a container format; it does not guarantee that every video encoding inside it is supported. The app does not claim to support every video format.
- Highlights and colors in some HDR footage may look different from the source. The current version does not guarantee preservation of HDR appearance.
- Saving a Live Photo and setting a lock-screen live wallpaper are separate actions. The app creates and saves Live Photos but does not set wallpapers. Compatibility as a lock-screen wallpaper on specific devices and OS versions has not been verified and is not guaranteed.

## Video demonstration

[Watch the real app-operation recording](https://hugehard.app/assets/video-to-live-photo-demo.mp4). It was captured in the project’s simulator promotion workflow with waiting portions edited out. The 19-second clip length is not a conversion-time measurement. The recording shows a simulator interface; the current beta may differ.

## Related pages

- [Product overview](https://hugehard.app/en/apps/this-pic-can-change/)
- [Product support](https://hugehard.app/en/apps/this-pic-can-change/support.html)
- [HTML guide](https://hugehard.app/en/guides/video-to-live-photo/)
