import { useState } from "react";
import { Activity, Plus, Gift, Award, Users } from "lucide-react";
import { Button, DataTable, Badge, Modal, Field, Select, Tabs } from "../ui";

export function AdminSurveys({ onToast }: { onToast: (msg: string) => void }) {
  const [tab, setTab] = useState("Опросы");
  const [showModal, setShowModal] = useState(false);
  const [surveys, setSurveys] = useState([
    { id: "1", title: "Что для вас важно в льготах?", participants: "412", date: "Сентябрь 2025", status: "Активен" },
    { id: "2", title: "Оценка удовлетворённости ДМС", participants: "890", date: "Август 2025", status: "Завершён" },
  ]);
  const [lotteries, setLotteries] = useState([
    { id: "1", title: "Осенняя лотерея 2025", pool: "30 000 б.", drawDate: "15.10.2025", participants: "1 248", status: "Идёт сбор" },
    { id: "2", title: "Летний розыгрыш призов", pool: "25 000 б.", drawDate: "15.06.2025", participants: "980", status: "Завершён" },
  ]);

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">АКТИВНОСТИ</span>
          <h1>Опросы, лотереи и геймификация (АДМ-20)</h1>
          <p>Конструктор опросов, мониторинг прохождения, розыгрыши и бейджи</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus size={17} /> Новый опрос
        </Button>
      </div>

      <div className="surface-card">
        <Tabs items={["Опросы", "Лотереи", "Геймификация"]} value={tab} onChange={setTab} />
      </div>

      {tab === "Опросы" && (
        <div className="surface-card table-card">
          <DataTable
            rows={surveys}
            columns={[
              { key: "title", label: "Название опроса" },
              { key: "participants", label: "Прошли опрос" },
              { key: "date", label: "Период" },
              { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Активен" ? "success" : "neutral"}>{r.status}</Badge> },
            ]}
            onRow={r => onToast(`Опрос: ${r.title}`)}
          />
        </div>
      )}

      {tab === "Лотереи" && (
        <div className="surface-card table-card">
          <DataTable
            rows={lotteries}
            columns={[
              { key: "title", label: "Розыгрыш" },
              { key: "pool", label: "Призовой фонд" },
              { key: "drawDate", label: "Дата розыгрыша" },
              { key: "participants", label: "Участников" },
              { key: "status", label: "Статус", render: r => <Badge tone={r.status.startsWith("Идёт") ? "warning" : "success"}>{r.status}</Badge> },
            ]}
          />
        </div>
      )}

      {tab === "Геймификация" && (
        <div className="generic-grid">
          <div className="generic-card">
            <span className="tile-icon"><Award size={23} /></span>
            <strong>Бейдж «Амбассадор знаний»</strong>
            <span>Награждено: 142 сотрудника</span>
          </div>
          <div className="generic-card">
            <span className="tile-icon"><Gift size={23} /></span>
            <strong>Бейдж «Щедрая душа»</strong>
            <span>За благотворительность и переводы · 88 сотрудников</span>
          </div>
        </div>
      )}

      {showModal && (
        <Modal
          title="Конструктор нового опроса"
          onClose={() => setShowModal(false)}
          footer={<Button className="full" onClick={() => { setShowModal(false); onToast("Опрос успешно опубликован"); }}>Создать опрос</Button>}
        >
          <div className="form-stack">
            <Field label="Тема опроса" placeholder="Например, Оценка программ обучения" />
            <Select label="Целевой сегмент" value="Все сотрудники" onChange={() => {}} options={["Все сотрудники", "Продуктовая команда", "Разработка", "HR"]} />
            <label className="field">
              <span className="field-label">Вопрос №1</span>
              <input type="text" placeholder="Введите текст вопроса..." />
            </label>
          </div>
        </Modal>
      )}
    </>
  );
}
