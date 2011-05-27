var enable_voting = function() {
	var new_rank = '<div class="ranking"><input type="number" class="rankvalue" value="{val}"></div>';
	
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			var target = $(event.target);
			var refilled = false;
			var newval = target.find('.rankvalue').val();
			ui.item.find('input').val(newval);
			
			var next = target.next();
			if (!next.is(".ranking")) {
				target.after(new_rank.replace("{val}", Number(newval) + 1));
				refilled = true;
			} else if (next.has(".candidate").length) {
				target.after(new_rank.replace("{val}", Number(newval) + 1));
				refilled = true;
			}
			
			var prev = target.prev();
			if (!prev.is(".ranking")) {
				target.before(new_rank.replace("{val}", Number(newval) - 1));
				refilled = true;
			} else if (prev.has(".candidate").length) {
				target.before(new_rank.replace("{val}", Number(newval) - 1));
				refilled = true;
			}
			
			if (refilled) {
				enable_voting();
			}
		}
	}).disableSelection();
};
