$("#name").qtip({
	content: {
		text: $("#logout")
	},
	position: {
		my: 'top center',
		at: 'bottom center',
		target: $('#name')
	},
	hide: {
		delay: 300,
		fixed: true,
		effect: function(offset) {
			$(this).slideUp(100);
		}
	},
	style: {
		classes: 'qtip-tipped'
	},
	show: {
		effect: function(offset) {
			$(this).slideDown(100);
		}
	}
})
