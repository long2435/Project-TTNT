// Hàm debounce đơn giản
function debounce(func, delay = 200) {
	let timer;
	return function (...args) {
		clearTimeout(timer);
		timer = setTimeout(() => func.apply(this, args), delay);
	};
}

// Lấy CSRF token từ cookie
function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

// Hàm gửi request cập nhật giỏ hàng
function updateCart(productId, action) {
	fetch('/update_item/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({ productId: productId, action: action })
	})
	.then(response => response.json())
	.then(data => {
		console.log('Success:', data);
		location.reload();
	});
}

// Áp dụng debounce cho từng nút update-cart
document.querySelectorAll('.update-cart').forEach(button => {
	const debouncedClick = debounce(function () {
		const productId = this.dataset.product;
		const action = this.dataset.action;
		updateCart(productId, action);
	}, 250); // Độ trễ 250ms để tránh double click

	button.addEventListener('click', debouncedClick);
});


// ✅ Tự động gửi request khi thay đổi số lượng (không cần submit form)
document.querySelectorAll('.quantity-input').forEach(input => {
	const debouncedChange = debounce(function () {
		const form = this.closest('.update-quantity-form');
		const productId = form.dataset.product;
		const quantity = this.value;

		fetch('/update_item/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
				'X-CSRFToken': getCookie('csrftoken'),
			},
			body: `productId=${productId}&quantity=${quantity}`,
		})
		.then(response => response.json())
		.then(data => {
			location.reload(); // Cập nhật lại trang giỏ hàng
		});
	}, 300); // debounce để tránh gửi liên tục khi người dùng gõ số

	input.addEventListener('change', debouncedChange);
});
