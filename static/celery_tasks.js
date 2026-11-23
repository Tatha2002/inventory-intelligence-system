
$(document).ready(function () {
    $("#inventory-upload-form").on("submit", function (event) {
        event.preventDefault();

        const form = this;
        const formData = new FormData(form);

        $("#upload-submit").prop("disabled", true);
        $("#upload-status").removeClass("alert-danger alert-success").addClass("alert-info").text("Uploading file and starting background task...").show();
        $("#upload-progress-container").show();
        $("#upload-progress-bar").css("width", "0%").text("0%");
        $("#upload-result").hide();

        $.ajax({
            url: $(form).attr("action"),
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                $("#upload-status").text(response.message);
                pollInventoryTask(response.task_id);
            },
            error: function (xhr) {
                let message = xhr.responseJSON?.message || "Unable to upload the CSV file.";
                if (xhr.responseJSON?.errors) {
                    message = Object.values(xhr.responseJSON.errors).flat().map(error => error.message).join(", ");
                }
                $("#upload-status").removeClass("alert-info").addClass("alert-danger").text(message);
                $("#upload-submit").prop("disabled", false);
            }
        });
    });

    function pollInventoryTask(taskId) {
        const statusUrl = $("#inventory-upload-form").data("status-url-template").replace("__TASK_ID__", encodeURIComponent(taskId));

        $.ajax({
            url: statusUrl,
            type: "GET",
            dataType: "json",
            success: function (response) {
                if (response.status === "PROGRESS") {
                    updateUploadProgress(response.progress || 0, response.message || "Processing inventory...");
                } else if (response.status === "STARTED") {
                    updateUploadProgress(10, "Inventory task has started...");
                } else if (response.status === "PENDING") {
                    updateUploadProgress(5, "Waiting for a Celery worker...");
                } else if (response.status === "SUCCESS") {
                    updateUploadProgress(100, response.message || "Inventory upload completed.");
                    showUploadResult(response.result);
                    $("#upload-status").removeClass("alert-info").addClass("alert-success");
                    $("#upload-submit").prop("disabled", false);
                } else if (response.status === "FAILURE") {
                    $("#upload-status").removeClass("alert-info").addClass("alert-danger").text(response.message || "Inventory upload failed.");
                    $("#upload-submit").prop("disabled", false);
                } else {
                    updateUploadProgress(0, "Task status: " + response.status);
                }

                if (!["SUCCESS", "FAILURE"].includes(response.status)) {
                    setTimeout(function () {
                        pollInventoryTask(taskId);
                    }, 1000);
                }
            },
            error: function () {
                $("#upload-status").removeClass("alert-info").addClass("alert-danger").text("Unable to retrieve task status. Please check the server.");
                $("#upload-submit").prop("disabled", false);
            }
        });
    }

    function updateUploadProgress(progress, message) {
        $("#upload-status").text(message).show();
        $("#upload-progress-bar").css("width", progress + "%").text(progress + "%");
    }

    function showUploadResult(result) {
        if (!result) return;

        $("#result-total").text(result.total ?? 0);
        $("#result-valid").text(result.valid ?? 0);
        $("#result-updated").text(result.updated ?? 0);
        $("#result-invalid").text(result.invalid ?? 0);

        const errorsBody = $("#upload-errors-body");
        errorsBody.empty();

        if (result.errors && result.errors.length > 0) {
            result.errors.forEach(function (error) {
                const row = $("<tr>");
                $("<td>").text(error.row ?? "").appendTo(row);
                $("<td>").text(error.error ?? error.message ?? JSON.stringify(error)).appendTo(row);
                errorsBody.append(row);
            });
            $("#upload-errors-container").show();
        } else {
            $("#upload-errors-container").hide();
        }

        $("#upload-result").show();
    }
});



$(document).ready(function () {
    $("#nlp-analysis-form").on("submit", function (event) {
        event.preventDefault();

        const form = this;

        $("#nlp-analysis-button").prop("disabled", true);
        $("#nlp-task-status").removeClass("alert-danger alert-success").addClass("alert-info").text("Starting complaint analysis...").show();
        $("#nlp-progress-container").show();
        $("#nlp-progress-bar").css("width", "0%").text("0%");

        $.ajax({
            url: $(form).attr("action"),
            type: "POST",
            data: $(form).serialize(),
            success: function (response) {
                $("#nlp-task-status").text(response.message);
                pollNLPTask(response.task_id);
            },
            error: function (xhr) {
                $("#nlp-task-status").removeClass("alert-info").addClass("alert-danger").text(xhr.responseJSON?.message || "Unable to start complaint analysis.");
                $("#nlp-analysis-button").prop("disabled", false);
            }
        });
    });

    function pollNLPTask(taskId) {
        const statusUrl = $("#nlp-analysis-form").data("status-url-template").replace("__TASK_ID__", encodeURIComponent(taskId));

        $.ajax({
            url: statusUrl,
            type: "GET",
            dataType: "json",
            success: function (response) {
                if (response.status === "PROGRESS") {
                    updateNLPProgress(response.progress || 0, response.message || "Processing complaints...");
                } else if (response.status === "PENDING") {
                    updateNLPProgress(5, "Waiting for a Celery worker...");
                } else if (response.status === "STARTED") {
                    updateNLPProgress(10, "Complaint analysis has started...");
                } else if (response.status === "SUCCESS") {
                    updateNLPProgress(100, response.message || "NLP analysis completed.");
                    $("#nlp-task-status").removeClass("alert-info").addClass("alert-success");
                    $("#nlp-analysis-button").prop("disabled", false);
                    setTimeout(function () {
                        window.location.reload();
                    }, 1500);
                    return;
                } else if (response.status === "FAILURE") {
                    $("#nlp-task-status").removeClass("alert-info").addClass("alert-danger").text(response.message || "NLP analysis failed.");
                    $("#nlp-analysis-button").prop("disabled", false);
                    return;
                }

                setTimeout(function () {
                    pollNLPTask(taskId);
                }, 1000);
            },
            error: function () {
                $("#nlp-task-status").removeClass("alert-info").addClass("alert-danger").text("Unable to retrieve NLP task status.");
                $("#nlp-analysis-button").prop("disabled", false);
            }
        });
    }

    function updateNLPProgress(progress, message) {
        $("#nlp-task-status").text(message).show();
        $("#nlp-progress-bar").css("width", progress + "%").text(progress + "%");
    }
});



$(document).ready(function () {

    $(".ml-prediction-form").on("submit", function (event) {

        event.preventDefault();

        const form = this;
        const button = $(form).find(".ml-predict-button");

        button.prop("disabled", true);

        $("#ml-task-container").show();

        $("#ml-task-title").text("Demand Prediction Processing");

        $("#ml-task-status")
            .removeClass("alert-danger alert-success")
            .addClass("alert-info")
            .text("Starting demand prediction...");

        $("#ml-progress-container").show();

        $("#ml-progress-bar")
            .removeClass("bg-success bg-danger")
            .addClass("progress-bar-striped progress-bar-animated")
            .css("width", "0%")
            .text("0%");

        $("#ml-prediction-result").hide();

        $.ajax({

            url: $(form).attr("action"),
            type: "POST",
            data: $(form).serialize(),
            dataType: "json",

            success: function (response) {

                if (response.success && response.task_id) {

                    $("#ml-task-status").text(response.message);

                    pollMLTask(response.task_id, form);

                } else {

                    $("#ml-task-status")
                        .removeClass("alert-info")
                        .addClass("alert-danger")
                        .text("Unable to start prediction.");

                    button.prop("disabled", false);
                }
            },

            error: function (xhr) {

                $("#ml-task-status")
                    .removeClass("alert-info")
                    .addClass("alert-danger")
                    .text(
                        xhr.responseJSON?.message ||
                        "Unable to start demand prediction."
                    );

                button.prop("disabled", false);
            }
        });
    });


    function pollMLTask(taskId, form) {

        const statusUrl = $(form)
            .data("status-url-template")
            .replace(
                "TASK_ID_PLACEHOLDER",
                encodeURIComponent(taskId)
            );

        $.ajax({

            url: statusUrl,
            type: "GET",
            dataType: "json",
            cache: false,

            success: function (response) {

                if (response.status === "PENDING") {

                    updateMLProgress(
                        5,
                        "Waiting for a Celery worker..."
                    );

                } else if (response.status === "STARTED") {

                    updateMLProgress(
                        10,
                        "Demand prediction started..."
                    );

                } else if (response.status === "PROGRESS") {

                    updateMLProgress(
                        response.progress || 0,
                        response.message
                    );

                } else if (response.status === "SUCCESS") {

                    const result = response.result;

                    if (result && result.success) {

                        updateMLProgress(
                            100,
                            "Demand prediction completed successfully."
                        );

                        $("#ml-task-title").text("Prediction Completed");

                        $("#ml-task-status")
                            .removeClass("alert-info alert-danger")
                            .addClass("alert-success")
                            .text(response.message);

                        $("#ml-result-product").text(result.product);

                        $("#ml-result-demand").text(
                            result.predicted_demand
                        );

                        $("#ml-result-risk").text(
                            result.reorder_risk
                        );

                        $("#ml-prediction-result").show();

                        $("#ml-progress-bar")
                            .removeClass(
                                "progress-bar-animated progress-bar-striped"
                            )
                            .addClass("bg-success");

                        setTimeout(function () {
                            window.location.reload();
                        }, 2000);

                    } else {

                        showMLFailure(
                            result?.message || "Prediction failed.",
                            form
                        );
                    }

                    return;

                } else if (response.status === "FAILURE") {

                    showMLFailure(response.message, form);
                    return;

                } else {

                    updateMLProgress(
                        0,
                        "Task status: " + response.status
                    );
                }

                setTimeout(function () {
                    pollMLTask(taskId, form);
                }, 1000);
            },

            error: function () {

                $("#ml-task-status")
                    .removeClass("alert-info")
                    .addClass("alert-danger")
                    .text("Unable to retrieve prediction status.");

                $(form)
                    .find(".ml-predict-button")
                    .prop("disabled", false);
            }
        });
    }


    function updateMLProgress(progress, message) {

        $("#ml-task-status").text(message);

        $("#ml-progress-bar")
            .css("width", progress + "%")
            .text(progress + "%");
    }


    function showMLFailure(message, form) {

        $("#ml-task-title").text("Prediction Failed");

        $("#ml-task-status")
            .removeClass("alert-info alert-success")
            .addClass("alert-danger")
            .text(message);

        $("#ml-progress-bar")
            .removeClass(
                "progress-bar-animated progress-bar-striped"
            )
            .addClass("bg-danger");

        $(form)
            .find(".ml-predict-button")
            .prop("disabled", false);
    }

});

