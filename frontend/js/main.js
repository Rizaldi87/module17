$.ajaxSetup({
  beforeSend: function beforeSend(xhr, settings) {
    function getCookies(name) {
      let cookieValue = null;

      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = jQuery.trim(cookies[i]);
          if (cookie.substring(0, name.length + 1) === `${name}=`) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }

      return cookieValue;
    }

    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      xhr.setRequestHeader("X-CSRFToken", getCookies("csrftoken"));
    }
  },
});

$(document)
  .on("click", ".js-toggle-modal", function (e) {
    e.preventDefault();
    $(".js-modal").toggleClass("hidden");
  })
  .on("click", ".js-submit", function (e) {
    e.preventDefault();
    const text = $(".js-post-text").val().trim();
    const $btn = $(this);

    if (!text.length) {
      return false;
    }

    $btn.prop("disabled", true).text("Posting!");
    $.ajax({
      type: "POST",
      url: $(".js-post-text").data("post-url"),
      data: { text: text },
      success: (dataHtml) => {
        $(".js-modal").addClass("hidden");
        $("#posts-container").prepend(dataHtml);
        $btn.prop("disabled", false).text("New Post");
        $(".js-post-text").val("");
      },
      error: (error) => {
        console.warn(error);
        $btn.prop("disabled", false).text("Error");
      },
    });
  });
$(".js-follow").on("click", function (e) {
  e.preventDefault();
  const action = $(this).attr("data-action");
  console.log("clicked");
  $.ajax({
    type: "POST",
    url: $(this).data("url"),
    data: {
      action: action,
      username: $(this).data("username"),
    },
    success: (data) => {
      $(".js-follow-text").text(data.wording);
      if (action === "follow") {
        $(this).attr("data-action", "unfollow");
      } else {
        $(this).attr("data-action", "follow");
      }
    },
    error: (error) => {
      console.warn(error);
    },
  });
});
