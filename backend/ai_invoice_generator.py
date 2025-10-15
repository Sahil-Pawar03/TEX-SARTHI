"""
TEX-SARTHI AI Invoice Generator
Advanced AI-powered invoice generation with natural language processing
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from models import Order, Customer, Invoice, Settings, db
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InvoiceItem:
    """Represents an item in an invoice"""
    description: str
    quantity: int
    unit_price: float
    total_price: float
    hsn_code: str = ""
    tax_rate: float = 0.18

@dataclass
class GeneratedInvoice:
    """Represents a generated invoice"""
    invoice_number: str
    customer_name: str
    customer_address: str
    items: List[InvoiceItem]
    subtotal: float
    tax_amount: float
    total_amount: float
    due_date: datetime
    notes: str = ""

class AIInvoiceGenerator:
    """AI-powered invoice generation system"""
    
    def __init__(self):
        self.textile_patterns = {
            "fabric_types": ["cotton", "silk", "polyester", "wool", "linen", "denim", "chiffon", "georgette"],
            "garment_types": ["shirt", "pant", "suit", "dress", "saree", "kurta", "salwar", "blouse"],
            "measurements": ["chest", "waist", "length", "sleeve", "inseam", "shoulder"],
            "services": ["tailoring", "alteration", "embroidery", "dyeing", "cleaning", "repair"]
        }
        
        self.tax_rates = {
            "fabric": 0.05,
            "readymade": 0.12,
            "tailoring": 0.18,
            "embroidery": 0.18
        }

    def analyze_order_content(self, order: Order) -> Dict:
        """Analyze order content using AI-like pattern matching"""
        analysis = {
            "category": "general",
            "complexity": "standard",
            "tax_rate": 0.18,
            "estimated_hours": 2,
            "material_cost_ratio": 0.6,
            "labor_cost_ratio": 0.4
        }
        
        order_text = f"{order.order_type} {order.fabric} {order.notes}".lower()
        
        # Analyze fabric type
        for fabric in self.textile_patterns["fabric_types"]:
            if fabric in order_text:
                if fabric in ["silk", "wool"]:
                    analysis["complexity"] = "premium"
                    analysis["tax_rate"] = 0.12
                elif fabric in ["cotton", "linen"]:
                    analysis["tax_rate"] = 0.05
                break
        
        # Analyze garment type
        for garment in self.textile_patterns["garment_types"]:
            if garment in order_text:
                if garment in ["suit", "saree"]:
                    analysis["complexity"] = "complex"
                    analysis["estimated_hours"] = 8
                elif garment in ["dress", "kurta"]:
                    analysis["estimated_hours"] = 4
                break
        
        # Analyze services
        for service in self.textile_patterns["services"]:
            if service in order_text:
                if service == "embroidery":
                    analysis["complexity"] = "complex"
                    analysis["estimated_hours"] *= 1.5
                elif service == "alteration":
                    analysis["estimated_hours"] *= 0.5
                break
        
        return analysis

    def generate_smart_invoice_items(self, order: Order, analysis: Dict) -> List[InvoiceItem]:
        """Generate intelligent invoice items based on order analysis"""
        items = []
        
        base_price = order.order_value
        
        # Main item (garment/fabric)
        main_item = InvoiceItem(
            description=f"{order.order_type.title()} - {order.fabric} ({order.color})",
            quantity=order.quantity,
            unit_price=base_price * analysis["material_cost_ratio"] / order.quantity,
            total_price=base_price * analysis["material_cost_ratio"],
            tax_rate=analysis["tax_rate"]
        )
        items.append(main_item)
        
        # Labor charges
        if analysis["complexity"] != "material_only":
            labor_item = InvoiceItem(
                description=f"Tailoring Services - {analysis['complexity'].title()} ({analysis['estimated_hours']}hrs)",
                quantity=1,
                unit_price=base_price * analysis["labor_cost_ratio"],
                total_price=base_price * analysis["labor_cost_ratio"],
                tax_rate=0.18
            )
            items.append(labor_item)
        
        # Additional services based on notes
        if order.notes:
            notes_lower = order.notes.lower()
            if "embroidery" in notes_lower:
                embr_item = InvoiceItem(
                    description="Custom Embroidery Work",
                    quantity=1,
                    unit_price=base_price * 0.2,
                    total_price=base_price * 0.2,
                    tax_rate=0.18
                )
                items.append(embr_item)
            
            if "alteration" in notes_lower:
                alt_item = InvoiceItem(
                    description="Alteration Services",
                    quantity=1,
                    unit_price=base_price * 0.1,
                    total_price=base_price * 0.1,
                    tax_rate=0.18
                )
                items.append(alt_item)
        
        return items

    def calculate_intelligent_pricing(self, items: List[InvoiceItem]) -> Tuple[float, float, float]:
        """Calculate intelligent pricing with tax optimization"""
        subtotal = sum(item.total_price for item in items)
        
        # Calculate tax amount with different rates
        tax_amount = 0
        for item in items:
            tax_amount += item.total_price * item.tax_rate
        
        total_amount = subtotal + tax_amount
        
        return subtotal, tax_amount, total_amount

    def generate_ai_notes(self, order: Order, analysis: Dict) -> str:
        """Generate intelligent notes based on order analysis"""
        notes = []
        
        if analysis["complexity"] == "premium":
            notes.append("Premium quality materials used.")
        elif analysis["complexity"] == "complex":
            notes.append("Complex tailoring work requiring expert craftsmanship.")
        
        if analysis["estimated_hours"] > 5:
            notes.append(f"Estimated completion time: {analysis['estimated_hours']} hours.")
        
        if order.delivery_date:
            days_to_delivery = (order.delivery_date - datetime.now().date()).days
            if days_to_delivery <= 3:
                notes.append("Rush order - expedited processing.")
            elif days_to_delivery > 14:
                notes.append("Standard processing timeline.")
        
        notes.append("Payment terms: 50% advance, balance on delivery.")
        
        return " ".join(notes)

    def generate_invoice_number(self) -> str:
        """Generate intelligent invoice number"""
        today = datetime.now()
        prefix = "TSI"  # TEX-SARTHI Invoice
        date_part = today.strftime("%Y%m%d")
        random_part = str(uuid.uuid4())[:6].upper()
        return f"{prefix}-{date_part}-{random_part}"

    def create_invoice_from_order(self, order_id: int, auto_calculate: bool = True) -> Optional[GeneratedInvoice]:
        """Create an AI-generated invoice from an order"""
        try:
            # Get order and customer data
            order = Order.query.get(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return None
            
            customer = Customer.query.get(order.customer_id)
            if not customer:
                logger.error(f"Customer {order.customer_id} not found")
                return None
            
            # AI analysis
            analysis = self.analyze_order_content(order)
            logger.info(f"AI Analysis for Order {order_id}: {analysis}")
            
            # Generate intelligent invoice items
            items = self.generate_smart_invoice_items(order, analysis)
            
            # Calculate pricing
            if auto_calculate:
                subtotal, tax_amount, total_amount = self.calculate_intelligent_pricing(items)
            else:
                subtotal = order.order_value
                tax_amount = subtotal * 0.18
                total_amount = subtotal + tax_amount
                # Adjust items to match order value
                if items:
                    adjustment_factor = subtotal / sum(item.total_price for item in items)
                    for item in items:
                        item.total_price *= adjustment_factor
                        item.unit_price *= adjustment_factor
            
            # Generate customer address
            customer_address = f"{customer.address or ''}, {customer.city or ''}, {customer.state or ''} {customer.pincode or ''}".strip(", ")
            
            # Generate AI notes
            ai_notes = self.generate_ai_notes(order, analysis)
            
            # Create generated invoice
            generated_invoice = GeneratedInvoice(
                invoice_number=self.generate_invoice_number(),
                customer_name=customer.name,
                customer_address=customer_address,
                items=items,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                due_date=datetime.now() + timedelta(days=30),
                notes=ai_notes
            )
            
            logger.info(f"Generated AI Invoice for Order {order_id}: {generated_invoice.invoice_number}")
            return generated_invoice
            
        except Exception as e:
            logger.error(f"Error generating invoice for order {order_id}: {str(e)}")
            return None

    def save_generated_invoice(self, generated_invoice: GeneratedInvoice, order_id: int) -> Optional[Invoice]:
        """Save the AI-generated invoice to database"""
        try:
            # Create invoice record
            invoice = Invoice(
                invoice_number=generated_invoice.invoice_number,
                order_id=order_id,
                customer_id=Order.query.get(order_id).customer_id,
                amount=generated_invoice.subtotal,
                tax_amount=generated_invoice.tax_amount,
                total_amount=generated_invoice.total_amount,
                status='pending',
                due_date=generated_invoice.due_date.date(),
                notes=generated_invoice.notes
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            logger.info(f"Saved AI-generated invoice {generated_invoice.invoice_number} to database")
            return invoice
            
        except Exception as e:
            logger.error(f"Error saving generated invoice: {str(e)}")
            db.session.rollback()
            return None

    def generate_invoice_description(self, order: Order) -> str:
        """Generate detailed invoice description using AI"""
        description_parts = []
        
        # Add main item description
        description_parts.append(f"Custom {order.order_type.title()}")
        
        if order.fabric:
            description_parts.append(f"in {order.fabric.title()}")
        
        if order.color:
            description_parts.append(f"({order.color.title()} Color)")
        
        if order.quantity > 1:
            description_parts.append(f"- Quantity: {order.quantity}")
        
        # Add measurement info if available
        if order.measurements:
            try:
                measurements = json.loads(order.measurements)
                if measurements:
                    description_parts.append("- Custom fitted with provided measurements")
            except:
                pass
        
        return " ".join(description_parts)

    def bulk_generate_invoices(self, order_ids: List[int]) -> List[GeneratedInvoice]:
        """Generate multiple invoices using AI"""
        generated_invoices = []
        
        for order_id in order_ids:
            invoice = self.create_invoice_from_order(order_id)
            if invoice:
                generated_invoices.append(invoice)
        
        logger.info(f"Bulk generated {len(generated_invoices)} invoices")
        return generated_invoices

# Initialize the AI generator
ai_invoice_generator = AIInvoiceGenerator()

# Utility functions for easy integration
def generate_ai_invoice(order_id: int, save_to_db: bool = True) -> Optional[GeneratedInvoice]:
    """Generate an AI-powered invoice for an order"""
    generated = ai_invoice_generator.create_invoice_from_order(order_id)
    
    if generated and save_to_db:
        ai_invoice_generator.save_generated_invoice(generated, order_id)
    
    return generated

def get_invoice_suggestions(order_id: int) -> Dict:
    """Get AI suggestions for invoice creation"""
    order = Order.query.get(order_id)
    if not order:
        return {}
    
    analysis = ai_invoice_generator.analyze_order_content(order)
    items = ai_invoice_generator.generate_smart_invoice_items(order, analysis)
    
    return {
        "analysis": analysis,
        "suggested_items": [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "tax_rate": item.tax_rate * 100  # Convert to percentage
            }
            for item in items
        ],
        "estimated_total": sum(item.total_price for item in items),
        "ai_notes": ai_invoice_generator.generate_ai_notes(order, analysis)
    }

if __name__ == "__main__":
    # Test the AI invoice generator
    print("TEX-SARTHI AI Invoice Generator Test")
    print("=" * 40)
    
    # This would be used for testing
    # test_order_id = 1  # Replace with actual order ID
    # result = generate_ai_invoice(test_order_id, save_to_db=False)
    # if result:
    #     print(f"Generated Invoice: {result.invoice_number}")
    #     print(f"Total Amount: ₹{result.total_amount:.2f}")
    # else:
    #     print("Failed to generate invoice")