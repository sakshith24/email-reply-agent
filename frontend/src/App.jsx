import { useEffect, useState } from "react";

const BACKEND_URL = "https://web-production-ad.up.railway.app"

export default function Dashboard() {
  const [drafts, setDrafts] = useState([]);
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [editedText, setEditedText] = useState("");


  useEffect(() => {
    fetch(`${BACKEND_URL}/api/drafts`)
      .then((res) => res.json())
      .then((data) => {
        setDrafts(data);
        if (data.length > 0) {
          setSelectedDraft(data[0]);
          setEditedText(data[0].ai_draft_content);
        }
      })
      .catch((err) => console.error("Error fetching drafts:", err));
  }, []);

  const handleSend = async () => {
    if (!selectedDraft) return;

    try {
      const res = await fetch(`${BACKEND_URL}/api/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: selectedDraft.id,
          recipient: selectedDraft.sender_email,
          final_content: editedText,
          subject: "Re: Your Inquiry",
        }),
      });

      if (res.ok) {
        alert("Email sent!");
        setDrafts(drafts.filter((d) => d.id !== selectedDraft.id));
        setSelectedDraft(null);
      }
    } catch (err) {
      console.error("Error sending draft:", err);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Pending Email Drafts</h1>
      {drafts.map((draft) => (
        <button
          key={draft.id}
          onClick={() => {
            setSelectedDraft(draft);
            setEditedText(draft.ai_draft_content);
          }}
          style={{ marginRight: 10, marginBottom: 10, display: "block" }}
        >
          {draft.sender_email} - {draft.user_query.slice(0, 30)}...
        </button>
      ))}

      {selectedDraft && (
        <div style={{ marginTop: 20 }}>
          <textarea
            rows={10}
            cols={60}
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
          />
          <br />
          <button onClick={handleSend} style={{ marginTop: 10 }}>
            Approve & Send Email
          </button>
        </div>
      )}
    </div>
  );
}