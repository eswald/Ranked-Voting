var enable_voting = function() {
	var new_rank = '<div class="ranking"><input type="number" class="rankvalue" value="0"></div>';
	
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			var target = $(event.target);
			var refilled = false;
			
			var next = target.next();
			if (!next.is(".ranking")) {
				target.after(new_rank);
				refilled = true;
			} else if (next.has(".candidate").length) {
				target.after(new_rank);
				refilled = true;
			}
			
			var prev = target.prev();
			if (!prev.is(".ranking")) {
				target.before(new_rank);
				refilled = true;
			} else if (prev.has(".candidate").length) {
				target.before(new_rank);
				refilled = true;
			}
			
			if (refilled) {
				enable_voting();
				$(".ranking").each(function(index, element) {
					$(element).find(".rankvalue").val(index + 1);
					$(element).find(".candidatevalue").val(index + 1);
				})
			} else {
				var newval = target.find('.rankvalue').val();
				ui.item.find('input').val(newval);
			}
		}
	}).disableSelection();
};
