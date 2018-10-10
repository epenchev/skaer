$(function () {
    var mediaCollections = []
    // $('.view-panel').removeClass('visible');

    $.getJSON( "media_collections.json", function( data ) {
        mediaCollections = data;
        generateMediaCollectionsHTML(mediaCollections);
        renderViewPanel(mediaCollections);
        // trace
        console.log('download media collections done');
    });

    function renderViewPanel(data) {
        var viewPanel = $('.view-panel'),
            collections = $('.view-panel .collections-list > li');

        // Hide all collections
        // collections.addClass('hidden');

        // Iterate over all of the collections
        // If their ID is somewhere in the data object remove the hidden class to reveal them.
        collections.each(function () {
		    var that = $(this);

            data.forEach(function (item) {
                console.log(item.id);
                console.log(that.data('index'));
                console.log("\n");
                if(that.data('index') == item.id) {
                    that.removeClass('hidden');
                    console.log('remove')
                }
            });
        });

        // Show the view-panel
        // (the render function hides all pages so we need to show the one we want).
        viewPanel.addClass('visible');
        collections = $('.view-panel .collections-list');
        collections.addClass('visible');
        console.log(collections.html());
    }

	function generateMediaCollectionsHTML(data) {
        var list = $('.view-panel .collections-list');
        var theTemplateScript = $("#collections-template").html();

        // Compile the template​
        var theTemplate = Handlebars.compile(theTemplateScript);
        list.append(theTemplate(data));
	}
});
