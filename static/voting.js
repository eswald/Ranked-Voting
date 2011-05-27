var enable_voting = function() {
	var new_rank = '<div class="ranking"><input type="number" class="rankvalue" value="0"></div>';
	
	$(".ranking").sortable({
		connectWith: ".ranking",
		receive: function(event, ui) {
			var target = $(event.target);
			var refilled = false;
			
			// Insert empty ranks where appropriate.
			var next = target.next();
			if (!next.is(".ranking") || next.has(".candidate").length) {
				target.after(new_rank);
				refilled = true;
			}
			
			var prev = target.prev();
			if (!prev.is(".ranking") || prev.has(".candidate").length) {
				target.before(new_rank);
				refilled = true;
			}
			
			// Remove empty ranks where appropriate.
			if (!ui.sender.has(".candidate").length) {
				next = ui.sender.next()
				if (next.is(".ranking") && !next.has(".candidate").length) {
					next.remove();
				}
				
				prev = ui.sender.prev()
				if (prev.is(".ranking") && !prev.has(".candidate").length) {
					prev.remove();
				}
			}
			
			// Update candidate values.
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
