var enable_voting = function() {
	var new_rank = '<div class="ranking"></div>';
	
	$(".ranking, .unranked").sortable({
		connectWith: ".ranking, .unranked",
		receive: function(event, ui) {
			var target = $(event.target);
			var refilled = false;
			
			// Insert empty ranks where appropriate.
			if (target.is(".ranking")) {
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
			}
			
			// Remove empty ranks where appropriate.
			if (ui.sender.is(".ranking") && !ui.sender.has(".candidate").length) {
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
			} else {
				var newval = target.data("rankvalue");
				ui.item.find('input').val(newval);
			}
		}
	}).disableSelection();
	
	$(".unranked").data("rankvalue", 0);
	$(".ranking").each(function (index, element) {
		$(element).data("rankvalue", index + 1).find(".candidatevalue").val(index + 1);
	});
};
