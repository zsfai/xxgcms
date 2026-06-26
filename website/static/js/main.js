var swiper = new Swiper('.swiper-container', {
    lazy: true,
    grabCursor: true,
    pagination: {
        el: '.swiper-pagination',
        clickable: true
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev'
    }
});