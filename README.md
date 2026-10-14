# HugeHard Studio 网站

这是 HugeHard Studio 的静态网站源码，使用原生 HTML、CSS 和少量图片资源，无需构建步骤；源码没有植入跟踪脚本。

## 已上线地址与配置

截至 2026 年 10 月 14 日，网站已通过 GitHub Pages 发布，并由 Cloudflare 提供域名解析与代理。

| 项目 | 当前配置 |
| --- | --- |
| 公开地址 | [https://hugehard.app](https://hugehard.app) |
| 独立公开仓库 | [`ilimei/hugehard-studio`](https://github.com/ilimei/hugehard-studio) |
| GitHub Pages | Legacy Pages，`main` 分支根目录；自定义域名 `hugehard.app` |
| `CNAME` | 仓库根目录内容为 `hugehard.app` |
| Cloudflare DNS | `@` 与 `www` 均为指向 `ilimei.github.io` 的 CNAME，当前均启用代理 |
| HTTPS | GitHub Pages 已强制 HTTPS；Cloudflare 使用 **Full (strict)**，**Always Use HTTPS** 已开启 |
| 证书与别名 | Cloudflare Universal Certificate 已启用，覆盖 `hugehard.app` 和 `www.hugehard.app`，有效期至 2027 年 1 月 12 日；`www` 重定向至 apex 域名 |
| 首次发布验收 | build `5b13225` 验收快照成功；当时验证 apex HTTPS 200，`www` 重定向至 HTTPS apex |

首次配置或重建自定义域名证书时，先按 GitHub Pages 文档在 Cloudflare 配置 `@` 和 `www` 记录，并将代理暂设为 **DNS only**。确认 GitHub Pages 检测到自定义域名并签发证书后，再启用 Cloudflare 代理；将 Cloudflare **SSL/TLS encryption mode** 设为 **Full (strict)**，开启 **Always Use HTTPS**，并在 GitHub Pages 设置中启用 **Enforce HTTPS**。

后续维护时，在独立站点仓库中编辑文件，提交并推送到 `main` 后会自动触发 GitHub Pages 部署。部署完成后可在仓库 Actions 中查看结果；不要用此仓库替换其他 GitHub Pages 站点或现有支持站点。

GitHub Pages 操作细节与 DNS 目标可能更新，请以 [发布源设置说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)和[自定义域名说明](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)为准。

## 客服邮箱显示

Cloudflare 默认的 Email Address Obfuscation 会在返回的页面中注入邮箱解码脚本。这是邮箱显示保护，不是站点跟踪脚本。`hugehardzhang@gmail.com` 是有意公开的业务联系邮箱，保持当前 Cloudflare 设置即可。

## SEO 与语言版本维护

本轮曝光优先围绕 iPhone 视频转 Live Photo / 视频转实况照片，入口统一指向现有规范指南 `/guides/video-to-live-photo/` 与英文镜像 `/en/guides/video-to-live-photo/`，不另建重复关键词页。《这图能改》继续标注准备上线；下载入口待取得并核实可用地址后再添加，不使用占位或猜测链接。

网站提供简体中文和英文两套页面。新增或修改成对页面时，按相同内容路径互链：中文在 `/` 与 `/apps/...`，英文在 `/en/` 与 `/en/apps/...`；教程对应放在 `/guides/` 和 `/en/guides/`。

- 每个可索引页面设置唯一且符合正文的 `title`、`description`、Open Graph 和 Twitter 标题、描述及图标；`og:url` 与自 canonical 一致。
- 每个中英文页面都设置指向自身的 canonical、对应语言的 `zh-Hans` 与 `en` alternate，以及指向中文对应页的 `x-default`。站内导航使用规范目录 URL 或实际 `.html` 文件地址，不链接 `index.html`。
- `sitemap.xml` 只列出 canonical 的可索引页面；不要加入 `404.html`。`robots.txt` 保持正常开放抓取。
- 结构化数据必须与可见文案一致：首页维护 `Organization` 与 `WebSite`，产品页使用 `WebPage`，并用共享 `Thing` 描述中文产品名与英文站点名称，教程维护 `Article` 与 `BreadcrumbList`。教程作者使用 HugeHard Studio，不添加虚构个人作者、价格、评分、下载链接或未经核实的统计。
- 目前产品准备上线，没有真实商店价格或应用评价，因此不标记 `SoftwareApplication` 富结果。Google 的该类富结果要求 `offers.price` 和 `rating` 或 `review`；等真实商品价格与评价可核实后，再按[官方规范](https://developers.google.com/search/docs/appearance/structured-data/software-app)评估是否添加。
- 教程需根据当前产品行为核实步骤、数值和限制。页面日期与 Article schema 中的日期同步更新；变更中英文页面时，同时更新对应语言路径。
- 搜索平台的站点验证、站点地图提交和收录状态需在平台中单独操作与核验；仅把带日期的平台返回状态记录在下文，不据此推断未检查页面的收录情况。

`/llms.txt` 是对 [llms.txt v2 提案](https://llmstxt.org/)的可读资料入口，链接四份精简中英文 Markdown 产品/指南文档和现有 HTML 页面。指定产品页与视频转实况指南通过 `rel="describedby"` 和 `rel="alternate" type="text/markdown"` 指向资料入口及对应 Markdown。它是自愿采用的提案格式，不是 Google 排名功能，也不保证索引或 AI 引用；Google 的[生成式 AI 内容指南](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)强调准确、优质且相关的内容。保持 Markdown 只复述已公开页面事实；同步修改时检查中英文 HTML、Markdown 与 `llms.txt`。`llms.txt` 和 `.md` 文件不加入 `sitemap.xml`。

## 视频演示素材

`assets/video-to-live-photo-demo.mp4` 来源于项目宣传用模拟器录屏，展示 App 的真实操作；等待片段已剪去。该录屏此前未在外部平台发布；19 秒是视频文件时长，不是转换用时。页面说明界面以准备发布的版本为准。

截至 2026 年 10 月 14 日的平台记录：[Google Search Console 属性](https://search.google.com/search-console?resource_id=sc-domain%3Ahugehard.app) `sc-domain:hugehard.app` 已通过 DNS 验证，站点地图重新提交后状态为 `Success`，报告发现 18 个 URL。发现 URL 不代表全部已收录；首页网址检查显示已收录，实时测试显示可编入索引。[Bing Webmaster Tools 站点地图](https://www.bing.com/webmasters/sitemaps?siteUrl=https%3A%2F%2Fhugehard.app%2F) 的 `https://hugehard.app/` 资源已通过 DNS 验证，站点地图状态仍为 `Processing`。发布新页面后重新提交并分别核对收录状态。

本地运行检查脚本：

```sh
python3 validate-site.py
```

脚本检查 canonical、hreflang 配对、站点地图、站内链接、`describedby`/Markdown 关联目标和 JSON-LD 语言与页面结构；也验证 `llms.txt` 与四份 Markdown 文档的同源链接。

## 本地预览

在网站仓库根目录运行 Python 自带的静态文件服务器：

```sh
python3 -m http.server 8000
```

然后在浏览器打开 `http://localhost:8000/`。检查中文和 `/en/` 首页、产品页、隐私/支持页、两种语言的指南索引与文章，以及 404 页面；试用键盘 Tab 导航与窄屏视图。再运行 `python3 validate-site.py`。按 Ctrl-C 关闭本地服务器。

## 页面与资源

- `index.html`：工作室首页。
- `apps/this-pic-can-change/`：产品介绍、隐私政策和使用支持。
- `en/` 与 `en/apps/this-pic-can-change/`：English 网站、产品、隐私与支持镜像。
- `guides/`、`en/guides/`：中英指南索引及图片压缩、视频转实况、截图交付教程。
- `llms.txt` 与四份 `index.md`：中英产品和视频转实况页面的精简机器可读资料。
- `assets/video-to-live-photo-demo.mp4`：视频转实况指南引用的本地录屏素材。
- `privacy.html`：本网站的数据处理，以及 Cloudflare 代理和 GitHub Pages 托管日志。
- `404.html`：站内未找到页面时显示。
- `assets/styles.css`：共享样式。
- `validate-site.py`：站点路由、SEO 元数据和结构化数据检查。
- `robots.txt`、`sitemap.xml`、`favicon.svg`、`.nojekyll`、`CNAME`：发布元数据与站点图标。
