// Populate the modal with existing data when editing
document.addEventListener('DOMContentLoaded', function () {
    var addEditModal = document.getElementById('addEditModal');
    addEditModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      var id = button.getAttribute('data-id');
      var name = button.getAttribute('data-name');
      var telephone = button.getAttribute('data-telephone');
      var idType = button.getAttribute('data-id_type');
      var idNumber = button.getAttribute('data-id_number');
  
      var modalTitle = addEditModal.querySelector('.modal-title');
      var formId = addEditModal.querySelector('#form-id');
      var formName = addEditModal.querySelector('#form-name');
      var formTelephone = addEditModal.querySelector('#form-telephone');
      var formIdType = addEditModal.querySelector('#form-id_type');
      var formIdNumber = addEditModal.querySelector('#form-id_number');
  
      modalTitle.textContent = id ? 'Edit Authorized Pick-Up' : 'Add Authorized Pick-Up';
      formId.value = id;
      formName.value = name;
      formTelephone.value = telephone;
      formIdType.value = idType;
      formIdNumber.value = idNumber;
    });
  });
  