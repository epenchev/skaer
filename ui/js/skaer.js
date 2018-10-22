$(function () {
    // Display all collections on page load
    showCollections('');
    // Install actions for main dropdown
    $('#videos').click(function() { showCollections('video'); return true; });
    $('#music').click(function() { showCollections('music'); return true; });

    function generateCollectionsHTML(data) {
        var list = $('.view-panel .collections-list');
        var theTemplateScript = $("#collections-template").html();

        // remove current elements from the list
        while (list.children('li').length) {
            list.children('li').remove();
        }
        // Compile the template​
        var theTemplate = Handlebars.compile(theTemplateScript);
        list.append(theTemplate(data));
    }

    // collType can be one of 'video', 'music' or '' for all types
    function showCollections(collType) {
        $('.view-panel').removeClass('visible');
        $('.collections-list').removeClass('visible');

        $.getJSON("/collections", function( data ) {
            if (collType != '') {
                var collIndex = 0;
                data.forEach(function (item) {
                    if (item.category.toLowerCase() != collType.toLowerCase())
                        data.splice(collIndex, 1);
                    collIndex += 1;
                });
            }
            generateCollectionsHTML(data);
            // Show the view-panel
            $('.view-panel').addClass('visible');
            $('.collections-list').addClass('visible');
        });
    }
});
