$(function () {

//This is shit code for drafting purposes.  Never do this.
    $("#lessDone").click(function () {
        $(".filled").last().attr("src", "content/progressbarsample/empty.jpg").removeClass("filled");
    });

    $("#moreDone").click(function () {
        $(".barIcon:not(.filled)").first().attr("src", "content/progressbarsample/filled.jpg").addClass("filled")
    });

});