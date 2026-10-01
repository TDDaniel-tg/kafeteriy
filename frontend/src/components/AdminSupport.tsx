import { useState } from "react";
import { LifeBuoy, Clock, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";
import { Button, DataTable, Badge, Drawer } from "../ui";

export function AdminSupport({ onToast }: { onToast: (msg: string) => void }) {
  const [tickets, setTickets] = useState([
    { id: "КЛ-1842", user: "Анна Морозова", subject: "Вопрос по сертификату Giftery", sla: "2 ч до SLA", status: "В обработке" },
    { id: "КЛ-1841", user: "Михаил Соколов", subject: "Задержка доставки мерча", sla: "6 ч до SLA", status: "Ожидает поставщика" },
    { id: "КЛ-1838", user: "Екатерина Волкова", subject: "Изменение программы ДМС", sla: "Соблюден", status: "Решено" },
    { id: "КЛ-1820", user: "Иван Васильев", subject: "Уточнение учетной записи (Exclusion)", sla: "Соблюден", status: "В обработке" },
  ]);
  const [selectedTicket, setSelectedTicket] = useState<any>(null);

  const resolveTicket = () => {
    if (!selectedTicket) return;
    setTickets(tickets.map(t => t.id === selectedTicket.id ? { ...t, status: "Решено" } : t));
    setSelectedTicket(null);
    onToast(`Обращение ${selectedTicket.id} успешно решено`);
  };

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ОБСЛУЖИВАНИЕ</span>
          <h1>Поддержка и SLA (ФТ-ПОД, АДМ-15)</h1>
          <p>Обращения сотрудников, контроль времени реакции и эскалация поставщикам</p>
        </div>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>В работе <LifeBuoy size={18} /></span>
          <strong>2 обращения</strong>
          <small>Требуют ответа специалиста</small>
        </div>
        <div className="kpi-card">
          <span>Соблюдение SLA <Clock size={18} /></span>
          <strong>98,4%</strong>
          <small>Норматив ответа: 24 часа</small>
        </div>
        <div className="kpi-card">
          <span>Среднее время ответа <CheckCircle2 size={18} /></span>
          <strong>1,8 часа</strong>
          <small>Значительно лучше целевого показателя</small>
        </div>
      </div>

      <div className="surface-card table-card">
        <DataTable
          rows={tickets}
          columns={[
            { key: "id", label: "Номер" },
            { key: "user", label: "Сотрудник" },
            { key: "subject", label: "Тема обращения" },
            { key: "sla", label: "Таймер SLA", render: r => <span className={r.sla.includes("2 ч") ? "text-amber-600 font-medium" : ""}>{r.sla}</span> },
            { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Решено" ? "success" : r.status === "Ожидает поставщика" ? "info" : "warning"}>{r.status}</Badge> },
          ]}
          onRow={r => setSelectedTicket(r)}
        />
      </div>

      {selectedTicket && (
        <Drawer
          title={`Обращение ${selectedTicket.id}`}
          onClose={() => setSelectedTicket(null)}
          footer={
            <div className="flex gap-2 w-full">
              <Button variant="secondary" className="w-1/2" onClick={() => { onToast("Повторный код сертификата отправлен"); }}>
                Выслать код повторно
              </Button>
              <Button className="w-1/2" onClick={resolveTicket}>
                Отметить как решено
              </Button>
            </div>
          }
        >
          <div className="form-stack">
            <div className="summary-row">
              <span>Сотрудник</span>
              <strong>{selectedTicket.user}</strong>
            </div>
            <div className="summary-row">
              <span>Тема</span>
              <strong>{selectedTicket.subject}</strong>
            </div>
            <div className="summary-row">
              <span>Статус SLA</span>
              <strong>{selectedTicket.sla}</strong>
            </div>
            <div className="surface-card bg-gray-50 text-sm">
              «Здравствуйте! Заказ оформлен, подскажите, когда поступит код на email? Не нахожу письмо в папке входящие.»
            </div>
            <label className="field">
              <span className="field-label">Ответ сотруднику</span>
              <textarea placeholder="Введите текст ответа поддержки..." rows={4} defaultValue="Здравствуйте! Повторно направили сертификат на вашу корпоративную почту. Пожалуйста, проверьте также папку Спам." />
            </label>
          </div>
        </Drawer>
      )}
    </>
  );
}
