import { useState } from "react";
import { Mail, Plus, Sparkles, BookOpen, Image, Megaphone } from "lucide-react";
import { Button, DataTable, Badge, Modal, Field, Select, Tabs } from "../ui";

export function AdminComms({ onToast }: { onToast: (msg: string) => void }) {
  const [tab, setTab] = useState("Новости");
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [news, setNews] = useState([
    { id: "1", title: "Осень — время для маленьких путешествий", date: "24.09.2025", comments: "12", status: "Опубликовано" },
    { id: "2", title: "Окно выбора льгот открыто до 15 октября", date: "15.09.2025", comments: "5", status: "Опубликовано" },
    { id: "3", title: "Новые программы английского языка от Skyeng", date: "01.09.2025", comments: "18", status: "Опубликовано" },
  ]);
  const [promos, setPromos] = useState([
    { id: "1", name: "Осенний кэшбэк на спорт", segment: "Все сотрудники", cashback: "10%", budget: "50 000 б.", spent: "32 000 б.", status: "Активна" },
    { id: "2", name: "Бонус ко Дню программиста", segment: "Разработка", cashback: "15%", budget: "30 000 б.", spent: "30 000 б.", status: "Завершена (исчерпан бюджет)" },
  ]);

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">КОММУНИКАЦИИ</span>
          <h1>Коммуникации и промо-акции (АДМ-19)</h1>
          <p>Новости, промо-баннеры, email-рассылки и промо-акции с кэшбэком</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus size={17} /> Создать публикацию
        </Button>
      </div>

      <div className="surface-card">
        <Tabs items={["Новости", "Промо-акции", "Баннеры", "Email-шаблоны"]} value={tab} onChange={setTab} />
      </div>

      {tab === "Новости" && (
        <div className="surface-card table-card">
          <DataTable
            rows={news}
            columns={[
              { key: "title", label: "Заголовок новости" },
              { key: "date", label: "Дата публикации" },
              { key: "comments", label: "Комментарии" },
              { key: "status", label: "Статус", render: r => <Badge tone="success">{r.status}</Badge> },
            ]}
            onRow={r => onToast(`Новость: ${r.title}`)}
          />
        </div>
      )}

      {tab === "Промо-акции" && (
        <div className="surface-card table-card">
          <DataTable
            rows={promos}
            columns={[
              { key: "name", label: "Название акции" },
              { key: "segment", label: "Сегмент" },
              { key: "cashback", label: "Кэшбэк" },
              { key: "budget", label: "Бюджет" },
              { key: "spent", label: "Израсходовано" },
              { key: "status", label: "Статус", render: r => <Badge tone={r.status.startsWith("Активна") ? "success" : "warning"}>{r.status}</Badge> },
            ]}
          />
        </div>
      )}

      {(tab === "Баннеры" || tab === "Email-шаблоны") && (
        <div className="generic-grid">
          <div className="generic-card">
            <span className="tile-icon"><Image size={23} /></span>
            <strong>Главный промо-баннер</strong>
            <span>Окно выбора льгот до 15 октября · Активен</span>
          </div>
          <div className="generic-card">
            <span className="tile-icon"><Mail size={23} /></span>
            <strong>Шаблон «Уведомление о сгорании баллов»</strong>
            <span>Отправка за 30 и 7 дней · Настроен</span>
          </div>
        </div>
      )}

      {showModal && (
        <Modal
          title="Новая публикация"
          onClose={() => setShowModal(false)}
          footer={<Button className="full" onClick={() => { setShowModal(false); onToast("Публикация создана и отправлена"); }}>Опубликовать</Button>}
        >
          <div className="form-stack">
            <Field label="Заголовок" value={title} onChange={setTitle} placeholder="Заголовок новости или рассылки" />
            <Select label="Тип" value="Новость" onChange={() => {}} options={["Новость", "Email-рассылка", "Промо-баннер"]} />
            <label className="field">
              <span className="field-label">Текст публикации</span>
              <textarea placeholder="Введите текст сообщения для сотрудников..." rows={4} />
            </label>
          </div>
        </Modal>
      )}
    </>
  );
}
