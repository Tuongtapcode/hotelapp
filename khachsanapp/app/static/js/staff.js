function loadFormContent(roomId, status, customerName = '', checkOutDate = '') {
    let content = '';
    if (status === 'Available') {
        content = `
                <h5>Đặt phòng hoặc Nhận phòng - P.${roomId}</h5>
                <form action="/booking" method="POST">
                    <div class="mb-3">
                        <label for="customerName" class="form-label">Tên khách hàng</label>
                        <input type="text" class="form-control" id="customerName" placeholder="Nhập tên khách hàng">
                    </div>
                    <div class="mb-3">
                        <label for="customer_identification_number" class="form-label">Số định danh</label>
                        <input type="text" class="form-control" id="customer_identification_number" placeholder="Số định danh">
                    </div>
                    <div class="d-grid gap-2">
                        <button type="button" class="btn btn-primary" onclick="handleBooking(${roomId})">Đặt phòng</button>
                        <button type="button" class="btn btn-success" onclick="handleCheckIn(${roomId})">Nhận phòng (Check-in)</button>
                    </div>
                </form>
            `;
    } else if (status === 'Booked') {
        content = `
                <h5>Nhận phòng hoặc Hủy đặt - P.${roomId}</h5>

                  <div class="d-grid gap-2">
                    <button class="btn btn-success" onclick="handleCheckIn(${roomId})">Nhận phòng (Check-in)</button>
                    <button class="btn btn-danger" onclick="handleCancelBooking(${roomId})">Hủy đặt phòng</button>
                </div>
            `;
    } else if (status === 'Checked') {
        content = `
                <h5>Trả phòng - P.${roomId}</h5>
                <form>
                    <div class="mb-3">
                        <label for="checkoutDate" class="form-label">Ngày trả phòng</label>
                        <input type="date" class="form-control" id="checkoutDate">
                    </div>
                    <button type="button" class="btn btn-danger" onclick="handleCheckout(${roomId})">Trả phòng</button>
                </form>
            `;
    } else {
        content = `<p>Không xác định trạng thái phòng.</p>`;
    }

    document.getElementById('modal-body-content').innerHTML = content;
}

function handleBooking(roomId) {
    console.log('handleCheckIn called with roomId:', roomId);
    const content = `
            <h5>Xác nhận đặt phòng - P.${roomId}</h5>
            <form>
                <div class="mb-3">
                    <label for="bookingDate" class="form-label">Ngày nhận phòng</label>
                    <input type="date" class="form-control" id="bookingDate">
                </div>
                <button type="submit" class="btn btn-primary">Xác nhận</button>
            </form>
        `;
    document.getElementById('modal-body-content').innerHTML = content;
}

function handleCheckIn(roomId) {
    fetch('/staff/rooms/checkin', { // Thay URL nếu có url_prefix
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({room_id: roomId})
    })
        .then(response => {
            if (!response.ok) { // Kiểm tra nếu HTTP status không phải 2xx
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            if (data.success) {
                location.reload(); // Reload lại danh sách phòng sau khi nhận phòng
            }
        })
        .catch(error => console.error('Error:', error));
}

function handleCancelBooking(roomId) {
    const content = `
            <h5>Xác nhận hủy đặt phòng - P.${roomId}</h5>
            <p>Bạn có chắc chắn muốn hủy đặt phòng này không?</p>
            <div class="d-grid gap-2">
                <button class="btn btn-danger">Hủy đặt phòng</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Thoát</button>
            </div>
        `;
    document.getElementById('modal-body-content').innerHTML = content;
}

function handleCheckout(roomId) {
    const content = `
            <h5>Xác nhận trả phòng - P.${roomId}</h5>
            <form >
                <div class="mb-3">
                    <label for="actualCheckoutDate" class="form-label">Ngày trả phòng thực tế</label>
                    <input type="date" class="form-control" id="actualCheckoutDate">
                </div>
                <button type="submit" class="btn btn-danger">Xác nhận</button>
            </form>
        `;
    document.getElementById('modal-body-content').innerHTML = content;
}

document.addEventListener("DOMContentLoaded", function () {
    const roomCards = document.querySelectorAll(".room-card");
    roomCards.forEach(function (card) {
        card.addEventListener("click", function () {
            const roomId = card.getAttribute("data-room-id");
            const roomStatus = card.getAttribute("data-room-status");

            loadFormContent(roomId, roomStatus);

            // Hiển thị Modal
            var myModal = new bootstrap.Modal(document.getElementById('roomModal'));
            myModal.show();
        });
    });
});
