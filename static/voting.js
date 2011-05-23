var enable_voting = function() {
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			ui.item.find('input').val($(event.target).find('input').val());
		}
	}).disableSelection();
};
