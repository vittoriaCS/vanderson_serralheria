var acc = document.getElementsByClassName("accordion");
for (var i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var panel = this.nextElementSibling;
        if (panel.style.display === "block") {
            panel.style.display = "none";
        } else {
            panel.style.display = "block";
        }
    });
}

document.querySelectorAll(".panel a").forEach(item => {
    item.addEventListener("click", function () {
       
        document.querySelectorAll(".content-box").forEach(box => {
            box.classList.add("hidden");
        });

        var targetId = this.getAttribute("data-target");
        document.getElementById(targetId).classList.remove("hidden");
    });
});

const statusField = document.getElementById("id_status");
const observacaoDiv = document.getElementById("div-observacao");
const devolucaoDiv = document.getElementById("div-devolucao");

function toggleCamposExtras() {
    const valor = statusField.value;
    if (valor === "devolvido" || valor === "danificado" || valor === "perdido") {
        observacaoDiv.style.display = "block";
        devolucaoDiv.style.display = "block";
    } else {
        observacaoDiv.style.display = "none";
        devolucaoDiv.style.display = "none";
    }
}

document.addEventListener('DOMContentLoaded', function() {
    toggleCamposExtras(); 
});

statusField.addEventListener('change', toggleCamposExtras);

function toggleUserMenu() {
    var dropdown = document.getElementById("user-dropdown");
    dropdown.classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.navbar-right, .navbar-right *')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
