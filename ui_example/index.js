$(document).ready(function () {
  $('.leftmenutrigger').on('click', function (e) {
    $('.side-nav').toggleClass("open");
    $('#wrapper').toggleClass("open");
    $('.side-nav').toggleClass("d-none");
    e.preventDefault();

    $('a').click(function(){
        $('a').removeClass("active");
        $(this).addClass("active");
    });
  });
});
