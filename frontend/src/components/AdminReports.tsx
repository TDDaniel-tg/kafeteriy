import { Download, FileSpreadsheet, CheckCircle2, ShieldAlert } from "lucide-react";
import { Button, DataTable, Badge } from "../ui";
import { api } from "../api";

export function AdminReports({ onToast }: { onToast: (msg: string) => void }) {
  const downloadAccounting = () => {
    window.open(api.getAccountingExportUrl(), "_blank");
    onToast("Формирование и загрузка выгрузки в бухгалтерию (CSV)");
  };

  const downloadPayouts = () => {
    window.open(api.getPayoutsExportUrl(), "_blank");
    onToast("Загрузка выгрузки «к выплате» для чековых компенсаций");
  };

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">БУХГАЛТЕРИЯ И ОТЧЁТЫ</span>
          <h1>Передача данных в бухгалтерию (АДМ-22)</h1>
          <p>Формирование регламентных реестров за период и ведомостей к выплате (ФТ-АНЛ.6, ФТ-АНЛ.7)</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={downloadAccounting}>
            <Download size={16} /> Выгрузка в бухгалтерию (ФТ-АНЛ.6)
          </Button>
          <Button variant="secondary" onClick={downloadPayouts}>
            <FileSpreadsheet size={16} /> Реестр «К выплате» (ФТ-АНЛ.7)
          </Button>
        </div>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>Сформировано заказов <FileSpreadsheet size={18} /></span>
          <strong>2 408 заказов</strong>
          <small>За текущий расчётный период</small>
        </div>
        <div className="kpi-card">
          <span>Валидация полей <CheckCircle2 size={18} /></span>
          <strong>100% корректно</strong>
          <small>ID, ФИО, город, телефон, тип лота, сумма</small>
        </div>
        <div className="kpi-card">
          <span>Ошибки выгрузки <ShieldAlert size={18} /></span>
          <strong>0 ошибок</strong>
          <small>Все поля проверены перед экспортом</small>
        </div>
      </div>

      <div className="surface-card">
        <h3>Состав выгрузки в бухгалтерию (ФТ-АНЛ.6)</h3>
        <p className="text-sm text-gray-500 mb-4">
          Файл формируется с точным набором реквизитов: ID заказа, ФИО, группа сотрудника, пол, дата рождения, город, телефон, наименование лота, тип товара, статус покупки, email, дата заказа, сумма заказа, комментарий, адрес доставки.
        </p>

        <DataTable
          rows={[
            { id: "1", field: "ID заказа", format: "Строка (КЛ-XXXXX)", required: "Да" },
            { id: "2", field: "ФИО сотрудника", format: "Строка (Фамилия Имя Отчество)", required: "Да" },
            { id: "3", field: "Группа / Сегмент", format: "Строка", required: "Да" },
            { id: "4", field: "Пол", format: "Мужской / Женский", required: "Да" },
            { id: "5", field: "Дата рождения", format: "ДД.ММ.ГГГГ", required: "Да" },
            { id: "6", field: "Город и телефон", format: "Строка", required: "Да" },
            { id: "7", field: "Наименование лота", format: "Текст", required: "Да" },
            { id: "8", field: "Тип товара", format: "Физический / Цифровой / Карта", required: "Да" },
            { id: "9", field: "Сумма заказа", format: "Целое число (баллы)", required: "Да" },
          ]}
          columns={[
            { key: "field", label: "Поле спецификации" },
            { key: "format", label: "Формат данных" },
            { key: "required", label: "Обязательность", render: r => <Badge tone="success">{r.required}</Badge> },
          ]}
        />
      </div>
    </>
  );
}
