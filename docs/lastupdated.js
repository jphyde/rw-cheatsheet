var txtFile = new XMLHttpRequest();
var allText = "file not found";
txtFile.onreadystatechange = function () {
  if (txtFile.readyState === XMLHttpRequest.DONE && txtFile.status == 200) {
    allText = txtFile.responseText;
    allText = allText.split("\n").join("<br>");
  }

  document.getElementById("upd-time").innerHTML = allText;
};
txtFile.open("GET", "updated.txt", true);
txtFile.send(null);
