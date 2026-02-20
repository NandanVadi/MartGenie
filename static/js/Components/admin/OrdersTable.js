import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Clock, XCircle } from 'lucide-react';

export default function OrdersTable({ orders }) {
  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      pending: 'bg-amber-100 text-amber-700 border-amber-200',
      failed: 'bg-red-100 text-red-700 border-red-200',
    };
    
    const icons = {
      completed: <CheckCircle2 className="w-3 h-3" />,
      pending: <Clock className="w-3 h-3" />,
      failed: <XCircle className="w-3 h-3" />,
    };

    return (
      <Badge variant="outline" className={`${styles[status]} flex items-center gap-1`}>
        {icons[status]}
        {status}
      </Badge>
    );
  };

  const getGatePassBadge = (used) => {
    return used ? (
      <Badge variant="outline" className="bg-emerald-100 text-emerald-700 border-emerald-200">
        Used
      </Badge>
    ) : (
      <Badge variant="outline" className="bg-slate-100 text-slate-600 border-slate-200">
        Pending
      </Badge>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div className="p-4 md:p-6 border-b border-slate-100">
        <h3 className="font-semibold text-slate-800">Recent Orders</h3>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50">
              <TableHead className="font-semibold">Order ID</TableHead>
              <TableHead className="font-semibold">Customer</TableHead>
              <TableHead className="font-semibold">Items</TableHead>
              <TableHead className="font-semibold">Amount</TableHead>
              <TableHead className="font-semibold">Payment</TableHead>
              <TableHead className="font-semibold">Gate Pass</TableHead>
              <TableHead className="font-semibold">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-slate-500">
                  No orders yet
                </TableCell>
              </TableRow>
            ) : (
              orders.map((order) => (
                <TableRow key={order.id} className="hover:bg-slate-50">
                  <TableCell className="font-medium text-slate-800">
                    {order.order_id}
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {order.customer_phone}
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {order.items?.length || 0} items
                  </TableCell>
                  <TableCell className="font-semibold text-slate-800">
                    ₹{order.total_amount?.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(order.payment_status)}
                  </TableCell>
                  <TableCell>
                    {getGatePassBadge(order.gate_pass_used)}
                  </TableCell>
                  <TableCell className="text-slate-500 text-sm">
                    {new Date(order.created_date).toLocaleTimeString('en-IN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}