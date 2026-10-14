# HugeHard Studio 网站

这是 HugeHard Studio 的待发布静态网站源码，使用原生 HTML、CSS 和少量图片资源，没有构建步骤或跟踪脚本。此目录只准备源码，不代表网站已经上线。

## 发布到 GitHub Pages

此目录的内容用于独立公开仓库 [`ilimei/hugehard-studio`](https://github.com/ilimei/hugehard-studio) 的 `main` 分支根目录。请将本目录中的全部内容放在该仓库根目录，并在 GitHub 仓库 **Settings → Pages → Build and deployment** 中选择 **Deploy from a branch**、`main` 和 `/(root)`，然后保存。

仓库根目录的 `CNAME` 文件指定 `hugehard.app`。还需在仓库 Pages 设置的 **Custom domain** 中填写 `hugehard.app` 并保存；`CNAME` 文件本身不会替代这个设置。

域名解析和代理由 Cloudflare 提供。请先按 GitHub Pages 当前文档在 Cloudflare 配置根域名记录，并将代理设为 **DNS only**；确认 GitHub Pages 检测到域名并签发证书后，再开启 Cloudflare 代理。启用代理后，将 Cloudflare **SSL/TLS encryption mode** 设为 **Full (strict)**。GitHub Pages 证书可用后，也可在仓库 Pages 设置中启用 **Enforce HTTPS**。

请把这个站点部署到上面指定的独立仓库，不要用它替换其他 GitHub Pages 仓库或现有支持站点。更改 `CNAME` 前先确认域名归属与目标仓库。本目录不表示 Pages 发布源、DNS 记录、代理或 HTTPS 证书已配置完成。

GitHub Pages 操作细节与 DNS 目标可能更新，请以 [发布源设置说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)和[自定义域名说明](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)为准。

## 本地预览

在网站仓库根目录运行 Python 自带的静态文件服务器：

```sh
python3 -m http.server 8000
```

然后在浏览器打开 `http://localhost:8000/`。检查首页、`/privacy.html`、`/apps/this-pic-can-change/` 及其 `privacy.html` 和 `support.html` 页面，并试用键盘 Tab 导航与窄屏视图。按 Ctrl-C 关闭本地服务器。

## 页面与资源

- `index.html`：工作室首页。
- `apps/this-pic-can-change/`：产品介绍、隐私政策和使用支持。
- `privacy.html`：仅说明本网站的数据处理与 GitHub Pages 托管日志。
- `404.html`：站内未找到页面时显示。
- `assets/styles.css`：共享样式。
- `robots.txt`、`sitemap.xml`、`favicon.svg`、`.nojekyll`、`CNAME`：发布元数据与站点图标。
