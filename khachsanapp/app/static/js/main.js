window.onscroll = function () {
    var header = document.querySelector(".header");
    var headerOffset = header.offsetTop;

    if (window.pageYOffset > headerOffset) {
        header.classList.add("header-sticky");
    } else {
        header.classList.remove("header-sticky");
    }

    // Kiểm tra khi người dùng lướt xuống 300px, hiển thị nút "Go to Top"
    var goTopButton = document.getElementById("gototop");
    if (window.pageYOffset > 300) {
        goTopButton.style.display = "block";
    } else {
        goTopButton.style.display = "none";
    }
};


document.addEventListener('DOMContentLoaded', function () {
    let list = document.querySelector('.anhchuyen .list');
    let items = document.querySelectorAll('.anhchuyen .list .item');
    let dots = document.querySelectorAll('.anhchuyen .dots li')
    let prev = document.getElementById('prev');
    let next = document.getElementById('next');


    if (next == null) {
        console.log('memay');
    } else {
        console.log('thanhcong');
    }
    let active = 0;
    let lengthItems = items.length - 1;
    prev.onclick = function () {
        if (active <= 0) {
            active = lengthItems;
        } else {
            active = active - 1;
        }
        reloadAnhchuyen();
    }

    next.onclick = function () {
        if (active >= lengthItems) {
            active = 0;
        } else {
            active = active + 1;
        }
        reloadAnhchuyen();
    }
    let refreshSlider = setInterval(() => {
        next.click()
    }, 5000);

    function reloadAnhchuyen() {
        let checkLeft = items[active].offsetLeft;
        console.log(checkLeft);
        list.style.left = -checkLeft + 'px';
        let lastActivedot = document.querySelector('.anhchuyen .dots li.active');
        lastActivedot.classList.remove('active');
        dots[active].classList.add('active');
        clearInterval(refreshSlider);
        refreshSlider = setInterval(() => {
            next.click()
        }, 5000);
    }

    dots.forEach((li, key) => {
        li.addEventListener('click', function () {
            active = key;
            reloadAnhchuyen();
        })
    })


});


$(document).ready(function () {
    function handleResponsiveNav() {
        $('div.menu-mobile').click(() => {
            $('.header-mobile ul.menu-mobile').toggleClass('show')
            console.log("helo1");
        })

    }

    handleResponsiveNav()
    $(window).scroll(function () {
        function addAnimationElementInWindow(element) {
            setTimeout(function () {
                let rect = element.getBoundingClientRect();
                let heightScreen = window.innerHeight;
                if (!(rect.bottom < 0 || rect.top > heightScreen)) {
                    element.classList.add('start');
                }
            }, 100);
        }

        function startAnimationScroll() {
            document.querySelectorAll('.scroll__right-to-left').forEach(function (element) {
                addAnimationElementInWindow(element);
            });
            document.querySelectorAll('.scroll__bot-to-top').forEach(function (element) {
                addAnimationElementInWindow(element);
            });
            document.querySelectorAll('.scroll__left-to-right').forEach(function (element) {
                addAnimationElementInWindow(element);
            });
            document.querySelectorAll('.scroll__hide-to-see').forEach(function (element) {
                addAnimationElementInWindow(element);
            });
        }

        startAnimationScroll();
    });
    // Gọi hàm startAnimationScroll() một lần nữa tại đây nếu bạn muốn chạy lúc ban đầu
});


const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
};

// Lấy đối tượng DOM
const checkinInput = document.getElementById('checkin');
const checkoutInput = document.getElementById('checkout');

// Lấy thời gian hiện tại
const now = new Date();
checkinInput.value = formatDateTime(now);

// Thiết lập checkout hơn checkin 1 ngày
const tomorrow = new Date(now);
tomorrow.setDate(tomorrow.getDate() + 1);
checkoutInput.value = formatDateTime(tomorrow);

// Lắng nghe sự kiện thay đổi trên checkin
checkinInput.addEventListener('change', () => {
    const checkinTime = new Date(checkinInput.value);
    const newCheckoutTime = new Date(checkinTime);
    newCheckoutTime.setDate(newCheckoutTime.getDate() + 1);
    checkoutInput.value = formatDateTime(newCheckoutTime);
});


