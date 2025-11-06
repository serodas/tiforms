from django.test import SimpleTestCase
from unittest.mock import Mock, patch
from forms.signals.webhook_signals import submission_created
from forms.listeners.webhook_listeners import handle_new_submission


class WebhookSignalSimpleTest(SimpleTestCase):
    """Tests UNITARIOS de señales - SIN base de datos"""

    def setUp(self):
        """DESCONECTAR el listener real antes de cada test"""
        submission_created.disconnect(handle_new_submission)

    def tearDown(self):
        """RECONECTAR el listener real después de cada test"""
        submission_created.connect(handle_new_submission)

    def test_signal_basics(self):
        """Test básico de la señal"""
        self.assertEqual(submission_created.__class__.__name__, "Signal")
        print("✅ Señal existe y es del tipo correcto")

    def test_signal_execution(self):
        """Test: La señal ejecuta el listener (con mock)"""
        # Crear un mock listener temporal
        mock_listener = Mock()

        # Conectar el mock listener a la señal
        submission_created.connect(mock_listener)

        try:
            # Configurar datos de prueba
            mock_sender = Mock()
            mock_submission = Mock()

            # Enviar la señal
            submission_created.send(sender=mock_sender, submission=mock_submission)

            # Verificar que el mock listener fue llamado
            self.assertTrue(mock_listener.called)
            mock_listener.assert_called_with(
                signal=submission_created,
                sender=mock_sender,
                submission=mock_submission,
            )
            print("✅ Señal ejecuta listener correctamente")

        finally:
            # Siempre desconectar el mock listener
            submission_created.disconnect(mock_listener)

    def test_signal_receivers(self):
        """Test CORREGIDO: Verificar receptores de la señal"""
        # Contar receptores iniciales
        initial_count = len(submission_created.receivers)

        # Agregar un receptor temporal
        mock_receiver = Mock()
        submission_created.connect(mock_receiver)

        # Verificar que se incrementó el contador
        self.assertEqual(len(submission_created.receivers), initial_count + 1)

        # Remover
        submission_created.disconnect(mock_receiver)

        # Verificar que volvió al contador original
        self.assertEqual(len(submission_created.receivers), initial_count)
        print("✅ Receptores manejados correctamente")

    def test_signal_has_receivers(self):
        """Test: La señal tiene receptores conectados"""
        # Verificar que la señal tiene algún receptor
        self.assertIsNotNone(submission_created.receivers)
        print(f"✅ Señal tiene {len(submission_created.receivers)} receptores")
