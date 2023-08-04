fetch("./updated.json")
  .then((response) => response.json())
  .then((json) => displayUpdStr(json));

function displayUpdStr(json) {
  var jsonDate = json["modifiedTime"];
  var displayTime = new Date(jsonDate);
  var options = {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: "false",
  };
  document.getElementById("upd-time").innerHTML = displayTime.toLocaleString(
    "en-US",
    options
  );
}
