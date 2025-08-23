import { useState } from "react";
import axios from "axios";

function App() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [imagem, setImagem] = useState(null);
  const [resposta, setResposta] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("nome", nome);
    formData.append("email", email);
    if (imagem) formData.append("imagem", imagem);

    try {
      const res = await axios.post("http://127.0.0.1:5000/submit", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResposta(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Formulário com Upload e Preview de Imagem</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            placeholder="Nome"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="file"
            onChange={(e) => setImagem(e.target.files[0])}
          />
        </div>
        <button type="submit" style={{ marginTop: "10px" }}>Enviar</button>
      </form>

      {resposta && (
        <div style={{ marginTop: "20px" }}>
          <h3>{resposta.mensagem}</h3>
          <p>Nome: {resposta.nome}</p>
          <p>Email: {resposta.email}</p>
          {resposta.arquivo && (
            <div>
              <p>Imagem enviada:</p>
              <img
                src={`http://127.0.0.1:5000/uploads/${resposta.arquivo}`}
                alt="Preview"
                style={{ maxWidth: "300px", marginTop: "10px" }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
