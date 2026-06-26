function returnTop() {
    (function smoothscroll() {
        var currentScroll = document.documentElement.scrollTop || document.body.scrollTop;
        if (currentScroll > 0) {
            window.requestAnimationFrame(smoothscroll);
            window.scrollTo(0, currentScroll - (currentScroll / 5));
        }
    })();
}

// 返回顶部函数 - 可以绑定到现有元素上
function backToTop() {
    // 平滑滚动到顶部
    if ('scrollBehavior' in document.documentElement.style) {
        // 支持平滑滚动
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    } else {
        // 不支持平滑滚动时使用原有的平滑滚动
        returnTop();
    }
}

// 页面加载完成后初始化返回顶部功能
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', backToTop);
} else {
    // backToTop();
}

function disallowCopy() {
    document.body.addEventListener("copy", function (e) {
        e.preventDefault();
        return false;
    })
}