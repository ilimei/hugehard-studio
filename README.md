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

## 本地预览

在网站仓库根目录运行 Python 自带的静态文件服务器：

```sh
python3 -m http.server 8000
```

然后在浏览器打开 `http://localhost:8000/`。检查首页、`/privacy.html`、`/apps/this-pic-can-change/` 及其 `privacy.html` 和 `support.html` 页面，并试用键盘 Tab 导航与窄屏视图。按 Ctrl-C 关闭本地服务器。

## 页面与资源

- `index.html`：工作室首页。
- `apps/this-pic-can-change/`：产品介绍、隐私政策和使用支持。
- `privacy.html`：本网站的数据处理，以及 Cloudflare 代理和 GitHub Pages 托管日志。
- `404.html`：站内未找到页面时显示。
- `assets/styles.css`：共享样式。
- `robots.txt`、`sitemap.xml`、`favicon.svg`、`.nojekyll`、`CNAME`：发布元数据与站点图标。
