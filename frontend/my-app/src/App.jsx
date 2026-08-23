import { useEffect, useState } from "react";
import toast from "react-hot-toast";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://web-production-88953.up.railway.app";

export default function Dashboard() {
  const [drafts, setDrafts] = useState([]);
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [editedText, setEditedText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    setIsLoading(true);

    fetch(`${BACKEND_URL}/api/drafts`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch drafts");
        }
        return res.json();
      })
      .then((data) => {
        setDrafts(data);

        if (data.length > 0) {
          setSelectedDraft(data[0]);
          setEditedText(data[0].ai_draft_content);
        }
      })
      .catch((err) => {
        console.error("Error fetching drafts:", err);
        toast.error("Failed to load drafts");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const handleSend = async () => {
    if (!selectedDraft) return;

    setIsSending(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json","x-api-key": import.meta.env.VITE_API_SECRET_KEY || "superkey123"},
        body: JSON.stringify({
          draft_id: selectedDraft.id,
          recipient: selectedDraft.sender_email,
          final_content: editedText,
          subject: "Re: Your Inquiry",
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();

        console.error("Backend error:", errorText);

        throw new Error(
          `Failed to send email (${res.status}): ${errorText}`
        );
      }

      toast.success("Email sent!");

      setDrafts((prevDrafts) =>
        prevDrafts.filter((d) => d.id !== selectedDraft.id)
      );

      setSelectedDraft(null);
      setEditedText("");
    } catch (err) {
      console.error("Error sending draft:", err);
      toast.error("Failed to send email");
    } finally {
      setIsSending(false);
    }
  };

  if (isLoading) {
    return <div style={{ padding: 20 }}>Loading drafts...</div>;
  }

  if (drafts.length === 0) {
    return (
      <div style={{ padding: 20 }}>
        <h1>Pending Email Drafts</h1>
        <p>All caught up! No drafts pending.</p>
      </div>
    );
  }

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
          style={{
            marginRight: 10,
            marginBottom: 10,
            display: "block",
          }}
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

          <button
            onClick={handleSend}
            disabled={isSending}
            style={{ marginTop: 10 }}
          >
            {isSending ? "Sending..." : "Approve & Send Email"}
          </button>
        </div>
      )}
    </div>
  );
}