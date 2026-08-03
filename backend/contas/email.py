class AdaptadorEmailConvite:
    """Contrato local para envio; SMTP fica pendente de decisao operacional."""

    def enviar(self, *, convite, token):
        # O token existe somente durante a chamada e nunca e salvo ou registrado.
        return {"status": "PENDENTE", "destinatario": convite.email}
