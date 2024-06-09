document.addEventListener("DOMContentLoaded", function () {
    // Format USD and JMD values
    document.querySelectorAll(".usd").forEach(function (element) {
      element.textContent = parseFloat(element.textContent).toLocaleString(
        "en-US",
        { minimumFractionDigits: 2, maximumFractionDigits: 2 }
      );
    });
    document.querySelectorAll(".jmd").forEach(function (element) {
      element.textContent = parseFloat(element.textContent).toLocaleString(
        "en-JM",
        { minimumFractionDigits: 2, maximumFractionDigits: 2 }
      );
    });
  
    // Sort the table rows by pounds
    const table = document.querySelector("table tbody");
    const rows = Array.from(table.querySelectorAll("tr"));
    rows.sort((a, b) => {
      const aPounds = parseFloat(a.querySelector("td").textContent);
      const bPounds = parseFloat(b.querySelector("td").textContent);
      return aPounds - bPounds;
    });
  
    // Append sorted rows to the table body
    rows.forEach(row => table.appendChild(row));
  });
  