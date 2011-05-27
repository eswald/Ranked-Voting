var enable_voting = function() {
	var new_rank = '<div class="ranking"><input type="number" class="rankvalue" value="{val}"></div>';
	
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			var target = $(event.target);
			var newval = target.find('.rankvalue').val();
			ui.item.find('input').val(newval);
			if (!target.next().is(".ranking")) {
				target.after(new_rank.replace("{val}", Number(newval) + 1));
				enable_voting();
			} else if (target.next().has(".candidate").length) {
				target.after(new_rank.replace("{val}", Number(newval) + 1));
				enable_voting();
			}
		}
	}).disableSelection();
};
