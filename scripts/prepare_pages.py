"""Prepare a self-contained GitHub Pages folder from the built static site."""

from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import shutil
import zipfile

from sync_static import copy_static


ROOT = Path(__file__).resolve().parents[1]


def prepare():

    source = ROOT / 'dist'
    target = ROOT / 'docs'

    target.mkdir(exist_ok=True)

    # --------------------------------------------------------
    # 顶层文件
    # --------------------------------------------------------

    for name in [
        'index.html',
        'visualizations.html',
        'behavior-analysis.html',
        'data-collection.html',
        'categories.html',
        'team.html',
        'LICENSE.txt'
    ]:

        copy_static(
            source / name,
            target / name
        )


    # --------------------------------------------------------
    # 文件夹
    # --------------------------------------------------------

    for name in [
        'assets',
        'spacemovement',
        'category-photos',
        'examples'
    ]:

        shutil.copytree(

            source / name,
            target / name,

            dirs_exist_ok=True,

            copy_function=copy_static,

            ignore=shutil.ignore_patterns(
                'sass',
                '*.xlsx',
                '*.docx',
                '*.py',
                '__pycache__'
            )

        )


    # GitHub Pages 不使用 Jekyll
    (target / '.nojekyll').write_text(
        '',
        encoding='utf-8'
    )


    # 验证生成结果
    verify(target)


    # --------------------------------------------------------
    # 打包 GitHub Pages
    # --------------------------------------------------------

    archive = (
        ROOT
        / '.site-build'
        / 'github-pages.zip'
    )

    archive.parent.mkdir(
        exist_ok=True
    )


    with zipfile.ZipFile(
        archive,
        'w',
        zipfile.ZIP_DEFLATED
    ) as z:

        for file in sorted(
            target.rglob('*')
        ):

            if file.is_file():

                z.write(
                    file,
                    file.relative_to(
                        target
                    ).as_posix()
                )


    print(
        'Prepared docs/ and '
        '.site-build/github-pages.zip'
    )


def verify(folder):

    count = 0


    # ========================================================
    # 检查本地资源链接
    # ========================================================

    def check(file, url):

        nonlocal count


        parsed = urlsplit(url)


        # 外部链接 / 空路径不检查
        if (
            parsed.scheme
            or parsed.netloc
            or not parsed.path
        ):
            return


        # GitHub project Pages 中禁止根路径链接
        assert not parsed.path.startswith('/'), (
            f'Root-relative URL breaks '
            f'project Pages: '
            f'{file}: {url}'
        )


        dest = (
            file.parent
            / unquote(parsed.path)
        ).resolve()


        # 链接不能逃出发布目录
        assert dest.is_relative_to(
            folder.resolve()
        ), (
            f'Link escapes publishing '
            f'folder: {url}'
        )


        # 文件必须存在
        assert dest.is_file(), (
            f'Missing resource: '
            f'{file}: {url}'
        )


        # ----------------------------------------------------
        # 检查文件名大小写
        # ----------------------------------------------------

        relative = dest.relative_to(
            folder.resolve()
        )

        parent = folder


        for part in relative.parts:

            assert part in [
                p.name
                for p in parent.iterdir()
            ], (
                f'Filename case mismatch: '
                f'{url}'
            )

            parent = parent / part


        count += 1


    # ========================================================
    # HTML 链接解析
    # ========================================================

    class Links(HTMLParser):

        def handle_starttag(
            self,
            tag,
            attrs
        ):

            for key, val in attrs:

                if (
                    key in ['src', 'href']
                    and val
                ):

                    check(
                        self.file,
                        val
                    )


    # ========================================================
    # 检查所有 HTML
    # ========================================================

    for file in folder.rglob(
        '*.html'
    ):

        parser = Links()

        parser.file = file

        parser.feed(
            file.read_text(
                encoding='utf-8-sig'
            )
        )


    # ========================================================
    # 检查所有 CSS url(...)
    # ========================================================

    for file in folder.rglob(
        '*.css'
    ):

        css = file.read_text(
            encoding='utf-8'
        )

        for url in re.findall(
            r'url\(\s*[\'"]?([^\)\'"\s]+)',
            css
        ):

            check(
                file,
                url
            )


    # ========================================================
    # 必须存在首页
    # ========================================================

    assert (
        folder / 'index.html'
    ).is_file()


    # ========================================================
    # 检查 visualizations.html 中的分析入口
    # ========================================================

    directory = (
        folder
        / 'visualizations.html'
    ).read_text(
        encoding='utf-8'
    )


    routes = re.findall(
        r'href="(spacemovement/[^"]+\.html)"',
        directory
    )


    from catalog import CATALOG


    # ========================================================
    # 正式页面：
    # CATALOG 中仍然只有 9 个 study
    #
    # route 本身例如：
    #
    # quality_vitality.html
    #
    # 但 visualizations.html 中实际 href 是：
    #
    # spacemovement/quality_vitality.html
    #
    # 所以这里统一补上 spacemovement/ 前缀。
    # ========================================================

    expected_routes = {

        f'spacemovement/{route}'

        for _, route, _, _ in CATALOG

    }


    # ========================================================
    # 新增：
    # “什么是不配得性？”说明页
    #
    # 它不是第 10 个 study，
    # 但它同样出现在 visualizations.html 中。
    # ========================================================

    expected_routes.add(
        'spacemovement/mismatch_intro.html'
    )


    # --------------------------------------------------------
    # 页面入口不得重复
    # --------------------------------------------------------

    assert len(routes) == len(
        set(routes)
    ), (
        'Duplicate visualization routes: '
        f'{routes}'
    )


    # --------------------------------------------------------
    # 必须恰好是：
    #
    # 9 个正式 study
    # +
    # 1 个 mismatch_intro
    # --------------------------------------------------------

    assert set(routes) == expected_routes, (

        'Visualization routes mismatch.\n'
        f'Actual: {sorted(set(routes))}\n'
        f'Expected: {sorted(expected_routes)}'

    )


    print(

        f'Verified {count} local HTML/CSS '
        f'resource links, exact filename case, '
        f'and all {len(CATALOG)} chart pages '
        f'plus mismatch introduction.'

    )


if __name__ == '__main__':

    prepare()