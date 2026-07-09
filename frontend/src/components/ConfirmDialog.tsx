import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

interface ConfirmContextType {
  confirm: (options: ConfirmOptions) => Promise<boolean>;
}

interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDanger?: boolean;
}

const ConfirmContext = createContext<ConfirmContextType | undefined>(undefined);

export const useConfirm = () => {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error('useConfirm must be used within a ConfirmProvider');
  }
  return context.confirm;
};

export const ConfirmProvider = ({ children }: { children: ReactNode }) => {
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState<ConfirmOptions>({ message: '' });
  const [resolvePromise, setResolvePromise] = useState<(value: boolean) => void>();

  const confirm = (opts: ConfirmOptions) => {
    setOptions(opts);
    setOpen(true);
    return new Promise<boolean>((resolve) => {
      setResolvePromise(() => resolve);
    });
  };

  const handleClose = (value: boolean) => {
    setOpen(false);
    if (resolvePromise) resolvePromise(value);
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <Dialog open={open} onClose={() => handleClose(false)}>
        <DialogTitle>{options.title || 'Confirm'}</DialogTitle>
        <DialogContent>
          <DialogContentText>{options.message}</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleClose(false)} color="inherit">
            {options.cancelText || 'Cancel'}
          </Button>
          <Button onClick={() => handleClose(true)} color={options.isDanger ? "error" : "primary"} variant="contained">
            {options.confirmText || 'Yes, Continue'}
          </Button>
        </DialogActions>
      </Dialog>
    </ConfirmContext.Provider>
  );
};
