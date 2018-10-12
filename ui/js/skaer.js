$(function () {
    var mediaCollections = []
    $.getJSON( "media_collections.json", function( data ) {
        mediaCollections = data;
        generateMediaCollectionsHTML(mediaCollections);
        renderViewPanel(mediaCollections);
    });

    function renderViewPanel(data) {
        // Iterate over all of the collections
        // If their ID is somewhere in the data object remove the hidden class to reveal them.
        collections.each(function () {
		    var that = $(this);

            data.forEach(function (item) {
                if( that.data('index') == item.id) {
                    that.removeClass('hidden');
                }
            });
        });

        // Show the view-panel
        // (the render function hides all pages so we need to show the one we want).
        $('.view-panel').addClass('visible');
        $('.collections-list').addClass('visible');
    }

	function generateMediaCollectionsHTML(data) {
        var list = $('.view-panel .collections-list');
        var theTemplateScript = $("#collections-template").html();

        // Compile the template​
        var theTemplate = Handlebars.compile(theTemplateScript);
        list.append(theTemplate(data));
	}
});
