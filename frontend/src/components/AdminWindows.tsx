import { useState } from "react";
import { CalendarDays, Plus, Clock, ShieldCheck, CheckCircle2 } from "lucide-react";
import { Button, DataTable, Badge, Modal, Field, DateField, Select, Toggle } from "../ui";

export function AdminWindows({ onToast }: { onToast: (msg: string) => void }) {
  const [windows, setWindows] = useState([
    { id: "1", name: "Осенний выбор льгот 2025", start: "2025-09-15", end: "2025-10-15", mode: "Информирует", status: "Открыто" },
    { id: "2", name: "Зимний выбор 2026", start: "2026-01-10", end: "2026-02-10", mode: "Ограничивает", status: "Запланировано" },
    { id: "3", name: "Летний выбор 2025", start: "2025-05-01", end: "2025-05-31", mode: "Информирует", status: "Архив" },
  ]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [startDate, setStartDate] = useState("2025-10-01");
  const [endDate, setEndDate] = useState("2025-10-31");
  const [ruleMode, setRuleMode] = useState("Информирует");
  const [error, setError] = useState("");

  const handleSave = () => {
    if (new Date(endDate) < new Date(startDate)) {
      setError("Дата окончания не может быть ранее даты начала (ФТ-ОКН.5).");
      return;
    }
    setError("");
    const newWin = {
      id: String(Date.now()),
      name: name || "Новое окно выбора",
      start: startDate,
      end: endDate,
      mode: ruleMode,
      status: "Открыто"
    };
    setWindows([newWin, ...windows]);
    setShowModal(false);
    onToast("Окно выбора успешно создано и активировано");
  };

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">КАМПАНИИ</span>
          <h1>Окна выбора (АДМ-18)</h1>
          <p>Управляйте периодами выбора льгот, продлением и режимами правил</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus size={17} /> Новое окно выбора
        </Button>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>Текущий период <CalendarDays size={18} /></span>
          <strong>Осенний выбор 2025</strong>
          <small>До 15 октября (остался 21 день)</small>
        </div>
        <div className="kpi-card">
          <span>Режим правил <ShieldCheck size={18} /></span>
          <strong>Информирует</strong>
          <small>Изменения разрешены с уведомлением</small>
        </div>
        <div className="kpi-card">
          <span>Уведомления <Clock size={18} /></span>
          <strong>Автоматически</strong>
          <small>Рассылка о старте и закрытии окна</small>
        </div>
      </div>

      <div className="surface-card table-card">
        <div className="card-heading">
          <div>
            <h3>Все кампании и периоды</h3>
            <p>Управление доступом сотрудников к изменению льгот</p>
          </div>
        </div>
        <DataTable
          rows={windows}
          columns={[
            { key: "name", label: "Название кампании" },
            { key: "start", label: "Дата начала" },
            { key: "end", label: "Дата окончания" },
            { key: "mode", label: "Режим правил", render: r => <Badge tone={r.mode === "Ограничивает" ? "danger" : "info"}>{r.mode}</Badge> },
            { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Открыто" ? "success" : "neutral"}>{r.status}</Badge> },
          ]}
          onRow={r => onToast(`Выбрано окно: ${r.name}`)}
        />
      </div>

      {showModal && (
        <Modal
          title="Создание окна выбора"
          onClose={() => setShowModal(false)}
          footer={<Button className="full" onClick={handleSave}>Сохранить и активировать</Button>}
        >
          <div className="form-stack">
            <Field label="Название кампании" value={name} onChange={setName} placeholder="Например, Осенний выбор льгот 2025" />
            <div className="field-pair">
              <DateField label="Дата начала" value={startDate} onChange={setStartDate} />
              <DateField label="Дата окончания" value={endDate} onChange={setEndDate} />
            </div>
            {error && <div className="text-red-500 text-sm">{error}</div>}
            <Select
              label="Режим правил изменения льгот"
              value={ruleMode}
              onChange={setRuleMode}
              options={["Информирует", "Ограничивает"]}
            />
            <p className="text-xs text-gray-500">
              В режиме «Ограничивает» вне периода окна оформление и отмена льгот блокируются.
            </p>
          </div>
        </Modal>
      )}
    </>
  );
}
