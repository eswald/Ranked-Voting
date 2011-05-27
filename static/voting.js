var enable_voting = function() {
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			var target = $(event.target);
			var newval = target.find('.rankvalue').val();
			ui.item.find('input').val(newval);
			if (!target.next().is(".ranking")) {
				target.after('<div class="ranking"><input type="number" class="rankvalue" value="{val}"></div>'.replace("{val}", Number(newval) + 1));
				enable_voting();
			}
		}
	}).disableSelection();
};
