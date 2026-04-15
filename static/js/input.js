document.getElementById("redirectmore").addEventListener("click", function (e) {
  e.preventDefault();
  const topic = this.getAttribute("data-llm-topic") || "general";
  window.open("/llm?topic=" + encodeURIComponent(topic), "_blank");
});