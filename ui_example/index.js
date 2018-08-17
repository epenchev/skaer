$(document).ready(function () {
  $('.leftmenutrigger').on('click', function (e) {
    $('.side-nav').toggleClass("open");
    $('#wrapper').toggleClass("open");
    $('.side-nav').toggleClass("d-none");
    e.preventDefault();
  });
});
